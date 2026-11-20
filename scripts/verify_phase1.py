import json
import os

processed_dir = r"c:\Users\Shoai\My Projects\DarGlobal-ai-chatbot\data\processed"
raw_dir = r"c:\Users\Shoai\My Projects\DarGlobal-ai-chatbot\data\raw"

print("=== RAW DIRECTORY CONTENTS ===")
for root, dirs, files in os.walk(raw_dir):
    for f in files:
        fp = os.path.join(root, f)
        print(f"  {os.path.relpath(fp, raw_dir)}: {os.path.getsize(fp):,} bytes")

print("\n=== PROCESSED DIRECTORY CONTENTS ===")
for root, dirs, files in os.walk(processed_dir):
    for f in files:
        fp = os.path.join(root, f)
        print(f"  {os.path.relpath(fp, processed_dir)}: {os.path.getsize(fp):,} bytes")

with open(os.path.join(processed_dir, "darglobal_documents.json"), encoding="utf-8") as f:
    dar_docs = json.load(f)

with open(os.path.join(processed_dir, "wasalt_documents.json"), encoding="utf-8") as f:
    wasalt_docs = json.load(f)

with open(os.path.join(processed_dir, "rag_chunks.json"), encoding="utf-8") as f:
    chunks = json.load(f)

with open(os.path.join(processed_dir, "extraction_log.json"), encoding="utf-8") as f:
    log = json.load(f)

print(f"\nTotal DarGlobal Documents: {len(dar_docs)}")
print(f"Total Wasalt Documents: {len(wasalt_docs)}")
print(f"Total Unified RAG Chunks: {len(chunks)}")

print("\n--- DarGlobal Documents Detail ---")
for d in dar_docs:
    print(f"[{d['id']}] {d['section']} | Title: {d['page_title']} | Lang: {d['language']} | Length: {len(d['content'])} chars")

print("\n--- Wasalt Documents Detail ---")
for d in wasalt_docs:
    print(f"[{d['id']}] {d['section']} | Title: {d['page_title'][:30]}... | Lang: {d['language']} | Length: {len(d['content'])} chars")

print("\n--- Unified Chunks Sample ---")
for c in chunks[:3]:
    print(f"Chunk ID: {c['chunk_id']} (from {c['doc_id']}) - Domain: {c['domain']}")
    print(f"Text Preview: {c['text'][:120]}...\n")

print("--- Extraction Limitations & Inaccessible Pages ---")
for p in log.get("inaccessible_pages", []):
    print(f"- {p['url']}: {p['reason']}")
