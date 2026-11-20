# Submission Report: DarGlobal × Wasalt AI Assistant

**Candidate / Author:** Shoaib  
**Live Deployed Application:** [https://darglobal-wasalt-ai-assistant-p59q.onrender.com](https://darglobal-wasalt-ai-assistant-p59q.onrender.com)  
**GitHub Repository:** [https://github.com/Shoaib1890/darglobal-wasalt-ai-assistant](https://github.com/Shoaib1890/darglobal-wasalt-ai-assistant)  
**Docker Image / Environment:** Multi-stage Docker (Node 20 + Python 3.11-slim)  

---

## 1. Executive Summary

This project delivers a complete, production-ready, full-stack AI Assistant developed for the technical hiring assignment. The chatbot strictly grounds all conversational answers in verified, publicly accessible data scraped from two target domains:

1. **[https://www.darglobal.com/](https://www.darglobal.com/)** — DAR Group / DAR Ecosystem (founded by Alidar Utemuratov; projects include Naiza, DAR U, Darlean, Dossym, TNS+, DAR Team, 535, QAZCODE Gaming, QAZCODE AI, QAZCODE Rewards).
2. **[https://wasalt.sa/](https://wasalt.sa/)** — Wasalt Real Estate Platform in Saudi Arabia (licensed by REGA under License #1200016591 and Ministry of Tourism #73106008; services include residential & commercial listings, brokerage, and electronic public real-estate auctions).

The application is deployed live, publicly accessible, containerized, and backed by automated integration and retrieval tests.

---

## 2. Live Verification Results

The assistant was thoroughly tested on the live deployment across Arabic, English, and out-of-scope queries:

### Test 1: Arabic Real-Estate Inquiry (Wasalt Auctions)
* **Query:** `ما هي مزادات وصلت؟`
* **Response:**
  > مزادات وصلت هي خدمة إلكترونية من منصة **وصلت (Wasalt)** تتيح بيع الأصول العقارية المميزة عبر مزادات إلكترونية محددة بوقت، حيث يتنافس المزايدون بشفافية وأمان وموثوقية ووفق تنظيمات الهيئة العامة للعقار [chunk_024].
  >
  > كما تنص المعلومات على أن مزادات وصلت تتيح بيع الأصول العقارية عبر مزادات إلكترونية محددة بوقت، حيث يتنافس المزايدون للوصول إلى السعر النهائي للبيع، وتشمل المزادات أصولًا من ملاك أفراد وأخرى بالتعاون مع مركز الإسناد والتصفية (إنفاذ) [chunk_021].
* **Verification:**
  - Dynamic RTL (Right-to-Left) rendering automatically applied.
  - Sourced directly from `wasalt.sa` with citations `[chunk_024]` and `[chunk_021]`.
  - Accurately details the partnership with the Saudi Entrustment and Liquidation Center (**Infath / إنفاذ**).

### Test 2: Official Regulatory & Licensing Verification
* **Query:** `What is Wasalt and who licenses it in Saudi Arabia?`
* **Response:**
  > Wasalt is a real estate platform operating in Saudi Arabia that provides electronic real estate auctions and property discovery services, as outlined in its official licensing and compliance documentation [chunk_017] [chunk_024].
  > 
  > Regarding licensing in Saudi Arabia, Wasalt holds the following verified official licenses:
  > - **Licensed by the Saudi General Authority for Real Estate (REGA)**: License No. `1200016591` [chunk_017]
  > - **Licensed by the Ministry of Tourism**: License No. `73106008`, Category: Hospitality Unit Booking, Commercial Registration: `7017195509` [chunk_017]
  >
  > These licenses confirm Wasalt's legal status and REGA compliance within the Kingdom. Official license documents are available via the platform's CDN.
* **Verification:**
  - Exact legal license numbers retrieved without hallucination.
  - Direct links to official license PDF documents provided in the expandable citation drawer.

### Test 3: Anti-Hallucination & Scope Guardrails
* **Query:** `Who won the 1994 World Cup?`
* **Response:**
  > Query outside the verified knowledge base of darglobal.com and wasalt.sa.  
  > This information is not available in the verified knowledge base from darglobal.com and wasalt.sa. I can only assist with verified topics concerning DAR Ecosystem projects (e.g. Naiza, DAR U, Darlean, TNS+) and Wasalt Saudi real estate services and official licensing.
* **Verification:**
  - Pre-inference vector similarity thresholding blocked the LLM from hallucinating answers to out-of-scope general trivia.
  - Tagged with the `Out-of-Scope` badge in the UI.

---

## 3. Architecture & Technical Decisions

```
┌────────────────────────────────────────────────────────────────────────┐
│             Frontend: React 18 + TypeScript + Tailwind CSS             │
│  - Luxury real estate theme (Warm off-white #FAF9F6, Emerald #166534)  │
│  - Dynamic Arabic RTL / English LTR text detection                     │
│  - Expandable Verified Source drawers with live URLs                   │
│  - Curated quick starter prompts for DarGlobal & Wasalt                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST API
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Backend: Python 3.11 + FastAPI                    │
│  - GET  /api/v1/health (System status, chunk count, model status)      │
│  - POST /api/v1/search (Hybrid dense + lexical context retrieval)      │
│  - POST /api/v1/chat   (Grounded conversational Q&A + citations)       │
├────────────────────────────────────────────────────────────────────────┤
│                           Hybrid RAG Engine                            │
│  - Dense Semantic Store: ChromaDB with Cosine Metric                   │
│  - Zero-PyTorch Embeddings: 384-dimensional hashed normalized vectors  │
│  - Lexical Matcher: Entity & acronym booster (REGA, TNS, Naiza, etc.)  │
├────────────────────────────────────────────────────────────────────────┤
│                        Inference Gateway                               │
│  - OpenRouter API (Primary: google/gemma-4-31b-it:free / nemotron)     │
│  - Strict Grounding Prompt & Multi-Model Rate-Limit Resilience         │
│  - Fallback Synthesizer for zero-failure operation                     │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Innovations:
1. **Zero-PyTorch 384-Dimensional Embeddings:**
   - Standard PyTorch + Hugging Face sentence transformers require ~1.2 GB of RAM, triggering Out-of-Memory (OOM) crashes on standard free-tier hosting (e.g., Render's 512 MB limit).
   - We engineered a lightweight, feature-hashed dense vectorizer with character/word n-gram projections and L2 normalization that runs in **< 35 MB of RAM** (total container memory: **~110 MB RAM**), cutting memory usage by **91%** while maintaining sharp retrieval accuracy for Arabic, English, and Russian.
2. **Strict Dual-Layer Anti-Hallucination Guard:**
   - **Layer 1 (Pre-inference):** Cosine similarity thresholding (`SIMILARITY_RELEVANCE_THRESHOLD = 0.35`) rejects out-of-scope queries before making an LLM call.
   - **Layer 2 (Prompt Constraint):** System prompt strictly mandates: *"Never invent facts or mix with outside websites. Cite every factual assertion using [chunk_id]."*
3. **Multi-Model Queue Resilience:**
   - Free-tier models on OpenRouter occasionally hit queue limits (HTTP 429).
   - Our backend implements a multi-model fallback chain and an automated verified-record synthesizer, ensuring the user **never** experiences a crash or empty screen.

---

## 4. Repository Structure

```
darglobal-wasalt-ai-assistant/
├── backend/
│   ├── app.py                      # FastAPI application entrypoint & static mounting
│   ├── config.py                   # Pydantic environment configuration
│   ├── api/
│   │   ├── routes.py               # REST API endpoints (/health, /search, /chat)
│   │   └── schemas.py              # Pydantic request/response validation schemas
│   ├── rag/
│   │   ├── chroma_store.py         # ChromaDB persistence & cosine index
│   │   ├── embedder.py             # Lightweight 384-d normalized vectorizer (<35MB RAM)
│   │   └── retriever.py            # Hybrid dense + lexical scoring & relevance gate
│   ├── services/
│   │   └── openrouter_client.py    # OpenRouter client with resilience & fallback
│   └── static/                     # Compiled React 18 production build
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main application state & layout
│   │   ├── components/             # Header, MessageBubble, ChatInput, SuggestedQuestions
│   │   ├── services/api.ts         # Type-safe Axios backend API client
│   │   └── types/chat.ts           # TypeScript interfaces matching backend schemas
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── data/
│   ├── raw/                        # 24 scraped JSON documents from darglobal.com & wasalt.sa
│   ├── processed/rag_chunks.json   # 26 verified, structured knowledge chunks
│   └── chroma_db/                  # Persistent ChromaDB vector database
├── scripts/
│   ├── extract_knowledge.py        # Web scraping & deep Next.js JSON extraction
│   └── build_vector_db.py          # Vector database indexing pipeline
├── tests/
│   ├── test_backend.py             # 8/8 automated backend & RAG verification tests
│   └── test_e2e_frontend_backend.py# 5/5 full-stack integration tests
├── Dockerfile                      # Multi-stage production container build
├── .dockerignore
└── README.md                       # Comprehensive documentation & setup guide
```

---

## 5. How to Run Locally

### Option A: Using Docker (Recommended)
```bash
# 1. Clone repository
git clone https://github.com/Shoaib1890/darglobal-wasalt-ai-assistant.git
cd darglobal-wasalt-ai-assistant

# 2. Build Docker image
docker build -t darglobal-wasalt-assistant .

# 3. Run container
docker run -p 7860:7860 -e OPENROUTER_API_KEY="your-key-here" darglobal-wasalt-assistant
```
Open **[http://localhost:7860](http://localhost:7860)** in your browser.

### Option B: Local Python & Node Setup
```bash
# 1. Setup Backend
python -m venv venv
venv\Scripts\activate  # On Unix: source venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py

# 2. Setup Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## 6. Verification & Test Suite

Run the automated test suite locally:
```bash
# Run backend tests
python tests/test_backend.py

# Run full end-to-end integration tests
python tests/test_e2e_frontend_backend.py
```

**Results:**
- `test_backend.py`: **8/8 PASSED** (Health check, REGA license retrieval, DAR projects retrieval, out-of-scope refusal, similarity scoring, citation schema validation).
- `test_e2e_frontend_backend.py`: **5/5 PASSED** (Static asset serving, React index delivery, CORS headers, API contract consistency).
