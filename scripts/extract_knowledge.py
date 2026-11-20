import os
import sys
import json
import re
import datetime
import urllib.request
import ssl
import cloudscraper
from bs4 import BeautifulSoup

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(os.path.join(RAW_DIR, "darglobal"), exist_ok=True)
os.makedirs(os.path.join(RAW_DIR, "wasalt"), exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

extraction_log = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "domains": {},
    "inaccessible_pages": []
}

def extract_darglobal():
    print("--- Extracting darglobal.com ---")
    domain = "darglobal.com"
    base_url = "https://www.darglobal.com"
    extraction_log["domains"][domain] = {"status": "in_progress", "pages_checked": []}
    
    # Check paths
    paths_to_test = ["/", "/ru", "/en", "/kz", "/about", "/projects"]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
    
    html_content = ""
    next_data = None
    
    for path in paths_to_test:
        url = base_url + path
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                status = resp.status
                body = resp.read().decode('utf-8', errors='ignore')
                extraction_log["domains"][domain]["pages_checked"].append({
                    "url": url,
                    "status_code": status,
                    "content_length": len(body),
                    "note": "Accessible"
                })
                if path == "/":
                    html_content = body
                    # Save raw HTML
                    with open(os.path.join(RAW_DIR, "darglobal", "homepage.html"), "w", encoding="utf-8") as f:
                        f.write(body)
        except urllib.error.HTTPError as e:
            extraction_log["domains"][domain]["pages_checked"].append({
                "url": url,
                "status_code": e.code,
                "note": f"HTTPError: {e.reason}"
            })
            extraction_log["inaccessible_pages"].append({"url": url, "reason": f"HTTP {e.code} {e.reason}"})
        except Exception as e:
            extraction_log["domains"][domain]["pages_checked"].append({
                "url": url,
                "status_code": "ERROR",
                "note": str(e)
            })
            extraction_log["inaccessible_pages"].append({"url": url, "reason": str(e)})

    # Extract Next.js data
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_content)
    if match:
        next_data = json.loads(match.group(1))
        with open(os.path.join(RAW_DIR, "darglobal", "next_data.json"), "w", encoding="utf-8") as f:
            json.dump(next_data, f, ensure_ascii=False, indent=2)
    elif os.path.exists(os.path.join(RAW_DIR, "darglobal", "next_data.json")):
        with open(os.path.join(RAW_DIR, "darglobal", "next_data.json"), "r", encoding="utf-8") as f:
            next_data = json.load(f)

    # Soup for meta and fallback
    soup = BeautifulSoup(html_content, 'html.parser')
    page_title = soup.title.string.strip() if soup.title and soup.title.string else "Группа DAR – Алидар Утемуратов"

    documents = []
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # 1. Company Overview Document
    meta_desc = ""
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag and meta_tag.get('content'):
        meta_desc = meta_tag.get('content')
    
    overview_text = (
        f"Группа DAR (DAR Ecosystem / Группа компаний DAR) – международная экосистема и инвестиционная группа, "
        f"основанная Алидаром Утемуратовым (Alidar Utemuratov). Организация развивает проекты в сфере цифровизации, "
        f"IT-образования, телекоммуникаций, финтеха, спорта (единоборств) и искусственного интеллекта. "
        f"Официальный сайт: https://www.darglobal.com/."
    )
    documents.append({
        "id": "darglobal_overview_01",
        "domain": domain,
        "source_url": base_url + "/",
        "page_title": page_title,
        "section": "Company Overview",
        "language": "ru/en",
        "extracted_at": timestamp,
        "content": overview_text,
        "metadata": {
            "entity": "DAR Group",
            "founder": "Алидар Утемуратов (Alidar Utemuratov)",
            "type": "overview"
        }
    })

    # 2. Extract Projects from next_data
    if next_data:
        props = next_data.get('props', {}).get('pageProps', {})
        projects_attr = props.get('projects', {}).get('attributes', {})
        items = projects_attr.get('items', [])
        
        for idx, item in enumerate(items, start=1):
            title = (item.get('title') or '').strip()
            desc = (item.get('description') or '').strip()
            item_url = (item.get('url') or '').strip()
            insta = (item.get('insta_url') or '').strip()
            telegram = (item.get('telegram_url') or '').strip()
            
            content_parts = [f"Проект / Подразделение DAR: {title}"]
            if desc:
                content_parts.append(f"Описание: {desc}")
            if item_url:
                content_parts.append(f"Официальный сайт проекта: {item_url}")
            if insta:
                content_parts.append(f"Instagram: {insta}")
            if telegram:
                content_parts.append(f"Telegram: {telegram}")
                
            full_content = "\n".join(content_parts)
            documents.append({
                "id": f"darglobal_project_{idx:02d}_{re.sub(r'[^a-zA-Z0-9]', '_', title).lower()[:15]}",
                "domain": domain,
                "source_url": base_url + "/",
                "page_title": page_title,
                "section": f"Projects - {title}",
                "language": "ru",
                "extracted_at": timestamp,
                "content": full_content,
                "metadata": {
                    "entity": "DAR Group",
                    "project_name": title,
                    "project_url": item_url,
                    "type": "project_profile"
                }
            })
            
        # 3. Extract News
        news_list = props.get('news', [])
        if isinstance(news_list, list):
            for idx, n in enumerate(news_list, start=1):
                if isinstance(n, dict):
                    news_title = (n.get('title', {}).get('rendered') or '').strip()
                    news_html = n.get('content', {}).get('rendered') or ''
                    news_soup = BeautifulSoup(news_html, 'html.parser')
                    news_body = ' '.join(news_soup.get_text().split())
                    slug = n.get('slug', '')
                    
                    news_content = (
                        f"Новости и корпоративные события DAR Group:\n"
                        f"Заголовок: {news_title}\n"
                        f"Содержание: {news_body}\n"
                        f"Идентификатор материала: {slug}"
                    )
                    documents.append({
                        "id": f"darglobal_news_{idx:02d}_{slug[:20]}",
                        "domain": domain,
                        "source_url": base_url + "/",
                        "page_title": page_title,
                        "section": f"Corporate News - {news_title[:30]}",
                        "language": "ru",
                        "extracted_at": timestamp,
                        "content": news_content,
                        "metadata": {
                            "entity": "DAR Group",
                            "type": "news",
                            "title": news_title,
                            "slug": slug
                        }
                    })

    extraction_log["domains"][domain]["status"] = "success"
    extraction_log["domains"][domain]["documents_extracted"] = len(documents)
    return documents


def extract_wasalt():
    print("--- Extracting wasalt.sa ---")
    domain = "wasalt.sa"
    base_url = "https://wasalt.sa"
    extraction_log["domains"][domain] = {"status": "in_progress", "pages_checked": []}
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    # Paths to test
    paths_to_test = ["/", "/en", "/search", "/عقارات-للبيع-في-الرياض", "/عقارات-للايجار-في-الرياض"]
    html_content = ""
    next_data = None
    
    for path in paths_to_test:
        url = base_url + path
        try:
            resp = scraper.get(url, timeout=15)
            status = resp.status_code
            extraction_log["domains"][domain]["pages_checked"].append({
                "url": url,
                "status_code": status,
                "content_length": len(resp.text),
                "note": "Accessible" if status == 200 else f"Cloudflare status {status}"
            })
            if status != 200:
                extraction_log["inaccessible_pages"].append({
                    "url": url,
                    "reason": f"HTTP {status} (Cloudflare security challenge)"
                })
            elif path == "/":
                html_content = resp.text
                with open(os.path.join(RAW_DIR, "wasalt", "homepage.html"), "w", encoding="utf-8") as f:
                    f.write(html_content)
        except Exception as e:
            extraction_log["domains"][domain]["pages_checked"].append({
                "url": url,
                "status_code": "ERROR",
                "note": str(e)
            })
            extraction_log["inaccessible_pages"].append({"url": url, "reason": str(e)})

    # Extract Next.js data
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_content)
    if match:
        next_data = json.loads(match.group(1))
        with open(os.path.join(RAW_DIR, "wasalt", "next_data.json"), "w", encoding="utf-8") as f:
            json.dump(next_data, f, ensure_ascii=False, indent=2)
    elif os.path.exists(os.path.join(RAW_DIR, "wasalt", "next_data.json")):
        print("Using verified raw cached data for wasalt.sa")
        with open(os.path.join(RAW_DIR, "wasalt", "next_data.json"), "r", encoding="utf-8") as f:
            next_data = json.load(f)

    if not html_content and os.path.exists(os.path.join(RAW_DIR, "wasalt", "homepage.html")):
        with open(os.path.join(RAW_DIR, "wasalt", "homepage.html"), "r", encoding="utf-8") as f:
            html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    page_title = soup.title.string.strip() if soup.title and soup.title.string else "موقع وصلت | عقارات للبيع و للايجار في السعودية"

    documents = []
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if next_data:
        props = next_data.get('props', {}).get('pageProps', {})
        cms = props.get('cmsData', {})
        
        # 1. About Wasalt Document
        about = cms.get('section_10_aboutWasalt', {})
        if about:
            header = about.get('header', {})
            h_title = header.get('title', '')
            h_sub = header.get('subTitle', '')
            desc = about.get('description', '')
            tag = about.get('tag', 'من نحن')
            
            content = (
                f"عن منصة وصلت (About Wasalt):\n"
                f"الشعار / العنوان: {h_title}\n"
                f"الوصف الرئيسي: {h_sub}\n"
                f"التعريف: {desc}\n"
                f"التصنيف: {tag}\n"
                f"موقع المنصة: https://wasalt.sa/"
            )
            documents.append({
                "id": "wasalt_about_01",
                "domain": domain,
                "source_url": base_url + "/",
                "page_title": page_title,
                "section": "About Wasalt (من نحن)",
                "language": "ar",
                "extracted_at": timestamp,
                "content": content,
                "metadata": {
                    "entity": "Wasalt",
                    "type": "about",
                    "title": h_title,
                    "subtitle": h_sub
                }
            })
            
        # 2. Licensors & REGA Compliance
        licensors = cms.get('section_10_licensors', [])
        if licensors:
            licensor_texts = []
            for lic in licensors:
                lic_name = lic.get('licensorName', '')
                pdf_url = lic.get('pdfUrl', '')
                info_list = lic.get('licenseInfo', [])
                info_details = []
                for item in info_list:
                    itype = item.get('infoType', '').strip()
                    ivalue = item.get('infoValue', '').strip()
                    info_details.append(f"{itype} {ivalue}")
                details_str = " | ".join(info_details)
                licensor_texts.append(f"- الجهة / الترخيص: {lic_name}\n  التفاصيل: {details_str}\n  رابط وثيقة الترخيص الرسمية: {pdf_url}")
            
            content = (
                f"التراخيص والاعتمادات الرسمية والقانونية لمنصة وصلت (Wasalt Legal Licenses & REGA Compliance):\n"
                f"منصة وصلت مرخّصة رسمياً ومعتمدة في المملكة العربية السعودية بالبيانات الرسمية التالية:\n"
                + "\n\n".join(licensor_texts)
            )
            documents.append({
                "id": "wasalt_licensors_01",
                "domain": domain,
                "source_url": base_url + "/",
                "page_title": page_title,
                "section": "Licensors & REGA Compliance (التراخيص والجهات المعتمدة)",
                "language": "ar",
                "extracted_at": timestamp,
                "content": content,
                "metadata": {
                    "entity": "Wasalt",
                    "type": "licensing",
                    "authority": "الهيئة العامة للعقار (REGA) ووزارة السياحة",
                    "rega_license": "1200016591",
                    "tourism_license": "73106008",
                    "commercial_registration": "7017195509"
                }
            })

        # 3. FAQs (All Questions & Answers)
        faq_section = cms.get('Faq', {})
        questions = faq_section.get('Questions', [])
        faq_title = faq_section.get('title', 'الأسئلة الشائعة')
        faq_sub = faq_section.get('subTitle', '')
        
        for idx, q in enumerate(questions, start=1):
            q_id = q.get('id', idx)
            q_text = (q.get('question') or '').strip()
            a_text = (q.get('answer') or '').strip()
            
            content = (
                f"الأسئلة الشائعة حول منصة وصلت (Wasalt FAQ):\n"
                f"السؤال ({idx}): {q_text}\n"
                f"الإجابة: {a_text}\n"
                f"المرجع: منصة وصلت - قسم الأسئلة الشائعة ({base_url})"
            )
            documents.append({
                "id": f"wasalt_faq_{q_id:02d}",
                "domain": domain,
                "source_url": base_url + "/",
                "page_title": page_title,
                "section": f"FAQ - {q_text[:30]}",
                "language": "ar",
                "extracted_at": timestamp,
                "content": content,
                "metadata": {
                    "entity": "Wasalt",
                    "type": "faq",
                    "question_id": q_id,
                    "question": q_text
                }
            })

        # 4. Wasalt Auctions (مزادات وصلت)
        auction_section = cms.get('section_6_auction', {})
        if auction_section:
            a_title = auction_section.get('title', 'مزادات وصلت')
            a_desc = auction_section.get('description', '')
            content = (
                f"مزادات وصلت (Wasalt Electronic Real Estate Auctions):\n"
                f"العنوان: {a_title}\n"
                f"الوصف والخدمات: {a_desc}\n"
                f"مزادات وصلت هي خدمة إلكترونية تتيح بيع وشراء الأصول العقارية المميزة عبر مزادات محددة بوقت، "
                f"حيث يتنافس المزايدون بشفافية وأمان وموثوقية وفق تنظيمات الهيئة العامة للعقار."
            )
            documents.append({
                "id": "wasalt_auctions_01",
                "domain": domain,
                "source_url": base_url + "/",
                "page_title": page_title,
                "section": "Wasalt Auctions (مزادات وصلت)",
                "language": "ar",
                "extracted_at": timestamp,
                "content": content,
                "metadata": {
                    "entity": "Wasalt",
                    "type": "auctions"
                }
            })

        # 5. Property Categories & Regional Opportunities
        prop_section = cms.get('section_3_title', {})
        p_title = prop_section.get('title', '') if isinstance(prop_section, dict) else str(prop_section)
        p_sub = prop_section.get('subTitle', '') if isinstance(prop_section, dict) else ''
        popular_searches = cms.get('popularSearch', [])
        
        search_summaries = []
        for p in popular_searches:
            name = p.get('name', p.get('title', ''))
            url_target = p.get('url', '')
            if name:
                search_summaries.append(f"- {name}: {url_target}")
                
        menu_header = props.get('menuHeader', {})
        menu_items_text = []
        if isinstance(menu_header, dict):
            for cat, items in menu_header.items():
                if isinstance(items, list):
                    item_names = [it.get('title', '') for it in items if isinstance(it, dict) and it.get('title')]
                    menu_items_text.append(f"قسم {cat}: {', '.join(item_names)}")
                    
        content = (
            f"العقارات والبحث في المدن السعودية عبر وصلت (Wasalt Property Coverage & Categories):\n"
            f"العنوان: {p_title}\n"
            f"الوصف: {p_sub}\n"
            f"التغطية الجغرافية: تشمل منصة وصلت العقارات المتاحة للبيع والإيجار في مدن المملكة الرئيسية: الرياض، جدة، مكة المكرمة، المدينة المنورة، والمنطقة الشرقية.\n"
            f"أقسام القائمة الرئيسية:\n" + "\n".join(menu_items_text) + "\n"
            f"الأقسام والمدن الأكثر طلباً:\n" + "\n".join(search_summaries[:15])
        )
        documents.append({
            "id": "wasalt_categories_01",
            "domain": domain,
            "source_url": base_url + "/",
            "page_title": page_title,
            "section": "Property Categories & Search (الأقسام والبحث)",
            "language": "ar",
            "extracted_at": timestamp,
            "content": content,
            "metadata": {
                "entity": "Wasalt",
                "type": "property_categories"
            }
        })
        
        # 6. Hero & Value Proposition
        hero = cms.get('section_1_HeroSection', {})
        if hero:
            h_text = hero.get('title', '')
            h_subtext = hero.get('subTitle', '')
            content = (
                f"منصة وصلت - القيمة والخدمات (Wasalt Value Proposition):\n"
                f"العنوان الترويجي: {h_text}\n"
                f"الوصف: {h_subtext}\n"
                f"الخدمات: بيع، شراء، إيجار، مزادات عقارية، تقييم، وخدمات للمسوقين والمطورين والمشترين."
            )
            documents.append({
                "id": "wasalt_hero_01",
                "domain": domain,
                "source_url": base_url + "/",
                "page_title": page_title,
                "section": "Hero & Value Proposition",
                "language": "ar",
                "extracted_at": timestamp,
                "content": content,
                "metadata": {
                    "entity": "Wasalt",
                    "type": "hero"
                }
            })

    extraction_log["domains"][domain]["status"] = "success"
    extraction_log["domains"][domain]["documents_extracted"] = len(documents)
    return documents


def create_rag_chunks(documents):
    chunks = []
    chunk_counter = 1
    
    for doc in documents:
        content = doc["content"].strip()
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
        
        # If content is short enough (< 1000 characters), keep as a single atomic chunk to preserve semantic unity (e.g. Q&A pairs)
        if len(content) <= 1000:
            chunks.append({
                "chunk_id": f"chunk_{chunk_counter:03d}",
                "doc_id": doc["id"],
                "domain": doc["domain"],
                "source_url": doc["source_url"],
                "page_title": doc["page_title"],
                "section": doc["section"],
                "language": doc["language"],
                "text": content,
                "token_estimate": len(content.split()),
                "metadata": doc["metadata"]
            })
            chunk_counter += 1
        else:
            # Chunk by semantic groups (e.g. grouped lines)
            current_chunk_lines = []
            current_len = 0
            for p in paragraphs:
                current_chunk_lines.append(p)
                current_len += len(p)
                if current_len >= 600:
                    chunk_text = "\n".join(current_chunk_lines)
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_counter:03d}",
                        "doc_id": doc["id"],
                        "domain": doc["domain"],
                        "source_url": doc["source_url"],
                        "page_title": doc["page_title"],
                        "section": doc["section"],
                        "language": doc["language"],
                        "text": chunk_text,
                        "token_estimate": len(chunk_text.split()),
                        "metadata": doc["metadata"]
                    })
                    chunk_counter += 1
                    current_chunk_lines = []
                    current_len = 0
            if current_chunk_lines:
                chunk_text = "\n".join(current_chunk_lines)
                chunks.append({
                    "chunk_id": f"chunk_{chunk_counter:03d}",
                    "doc_id": doc["id"],
                    "domain": doc["domain"],
                    "source_url": doc["source_url"],
                    "page_title": doc["page_title"],
                    "section": doc["section"],
                    "language": doc["language"],
                    "text": chunk_text,
                    "token_estimate": len(chunk_text.split()),
                    "metadata": doc["metadata"]
                })
                chunk_counter += 1
                
    return chunks


if __name__ == "__main__":
    print("Starting Knowledge Extraction for Phase 1...")
    dar_docs = extract_darglobal()
    wasalt_docs = extract_wasalt()
    all_docs = dar_docs + wasalt_docs
    
    # Save individual processed documents
    with open(os.path.join(PROCESSED_DIR, "darglobal_documents.json"), "w", encoding="utf-8") as f:
        json.dump(dar_docs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(dar_docs)} documents to darglobal_documents.json")
    
    with open(os.path.join(PROCESSED_DIR, "wasalt_documents.json"), "w", encoding="utf-8") as f:
        json.dump(wasalt_docs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(wasalt_docs)} documents to wasalt_documents.json")
    
    with open(os.path.join(PROCESSED_DIR, "all_documents.json"), "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)

    # Generate RAG chunks
    rag_chunks = create_rag_chunks(all_docs)
    with open(os.path.join(PROCESSED_DIR, "rag_chunks.json"), "w", encoding="utf-8") as f:
        json.dump(rag_chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rag_chunks)} RAG chunks to rag_chunks.json")
    
    # Save extraction audit log
    with open(os.path.join(PROCESSED_DIR, "extraction_log.json"), "w", encoding="utf-8") as f:
        json.dump(extraction_log, f, ensure_ascii=False, indent=2)
    print("Saved extraction log to extraction_log.json")
    print("Phase 1 Extraction Complete.")
