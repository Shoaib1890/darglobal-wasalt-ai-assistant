---
title: DarGlobal Wasalt AI Assistant
emoji: 🏢
colorFrom: green
colorTo: emerald
sdk: docker
app_port: 7860
pinned: false
---

# DarGlobal × Wasalt AI Assistant

A production-grade, bilingual AI chatbot built to answer inquiries using strictly verified, publicly accessible information scraped from:
1. **[https://www.darglobal.com/](https://www.darglobal.com/)** — DAR Group / DAR Ecosystem (founded by Alidar Utemuratov).
2. **[https://wasalt.sa/](https://wasalt.sa/)** — Wasalt Real Estate Platform in Saudi Arabia (licensed by REGA).

---

## 🌟 Key Features

* **Strict Grounding & Zero Fabrication:** Responses are generated exclusively from verified, structured knowledge chunks with citations mapped to exact chunk IDs and URLs.
* **Bilingual Support (Arabic & English):** Dynamic text direction handling (RTL for Arabic, LTR for English/Russian) across the UI.
* **Hybrid Multilingual RAG:**
  * **ChromaDB** persistent vector database.
  * **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** 384-dimensional normalized embeddings.
  * BM25 keyword boosting for high-priority regulatory and corporate entities (REGA License #1200016591, Naiza, DAR U, Darlean, TNS+).
* **Anti-Hallucination Guardrails:** Relevance filtering blocks out-of-scope queries (e.g. unrelated general knowledge) from calling the LLM.
* **OpenRouter Free LLM Integration:** Connects seamlessly to free-tier LLM models (`openrouter/free`, `google/gemma-4-31b-it:free`, `nvidia/nemotron-3.5-lightning:free`).
* **Offline / No-Key Graceful Mode:** If no `OPENROUTER_API_KEY` is supplied, the chatbot still functions reliably by synthesizing verified context directly with structured citations.
* **Self-Contained Full-Stack Container:** Multi-stage Docker build packaging both the FastAPI backend and the compiled React 18 TypeScript frontend into a single lightweight image (< 450 MB RAM).

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│             Frontend: React 18 + TypeScript + Tailwind CSS             │
│  - Luxury real estate theme (Warm off-white #FAF9F6, Emerald #166534)  │
│  - Dynamic Arabic RTL / English LTR text detection                     │
│  - Expandable Verified Source drawers with live URLs                   │
│  - Curated quick starter prompts for DarGlobal & Wasalt               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST API
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Backend: Python 3.11 + FastAPI                    │
│  - GET  /api/v1/health (System status, chunk count, model status)     │
│  - POST /api/v1/search (Hybrid dense + lexical context retrieval)      │
│  - POST /api/v1/chat   (Grounded conversational Q&A + citations)       │
├────────────────────────────────────────────────────────────────────────┤
│                           Hybrid RAG Engine                            │
│  - Dense Semantic Store: ChromaDB with Cosine Metric                   │
│  - Multilingual Embeddings: paraphrase-multilingual-MiniLM-L12-v2      │
│  - Lexical Matcher: Entity & acronym booster (REGA, TNS, Naiza, etc.)  │
├────────────────────────────────────────────────────────────────────────┤
│                        Inference Gateway                               │
│  - OpenRouter API (Primary: openrouter/free)                           │
│  - Grounded Context Assembly & Anti-Hallucination System Prompt        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Running Locally with Docker

### 1. Build the Docker Image
```bash
docker build -t darglobal-wasalt-assistant .
```

### 2. Run the Container
```bash
docker run -p 7860:7860 -e OPENROUTER_API_KEY="your-openrouter-key" darglobal-wasalt-assistant
```

Access the interface in your browser at:
👉 **[http://localhost:7860](http://localhost:7860)**

---

## ☁️ Deploying to Hugging Face Spaces (Free Tier)

This repository is pre-configured for instant deployment to Hugging Face Spaces using the Docker SDK:

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Set **Space Name** (e.g. `darglobal-wasalt-chatbot`).
3. Select **Docker** as the Space SDK (Choose the **Blank** template).
4. Push this repository's code to your Hugging Face Space repository:
   ```bash
   git remote add space https://huggingface.co/spaces/<YOUR_HF_USERNAME>/darglobal-wasalt-chatbot
   git push space main
   ```
5. In your Hugging Face Space settings (**Settings > Variables and Secrets**):
   * Add a new Secret:
     * **Name:** `OPENROUTER_API_KEY`
     * **Value:** `sk-or-v1-...` (Get a free key from [OpenRouter](https://openrouter.ai/))
6. Your space will automatically build and start on port **7860**, giving you a permanent public URL:
   `https://<YOUR_HF_USERNAME>-darglobal-wasalt-chatbot.hf.space`

---

## 🛠️ Environment Configuration

| Variable | Description | Default | Required? |
| :--- | :--- | :--- | :---: |
| `OPENROUTER_API_KEY` | API Key for OpenRouter free LLM inference | `""` (Empty) | Recommended |
| `OPENROUTER_MODEL` | Target OpenRouter LLM model | `openrouter/free` | No |
| `PORT` | Web server listening port | `7860` | No |
| `SIMILARITY_RELEVANCE_THRESHOLD` | Minimum score to consider query in-scope | `0.35` | No |
| `DEFAULT_TOP_K` | Number of context chunks retrieved | `4` | No |

---

## 🧪 Automated Test Suite

Run the end-to-end integration and RAG verification test suite:

```bash
# Backend unit & retrieval tests
python tests/test_backend.py

# End-to-end frontend + backend integration tests
python tests/test_e2e_frontend_backend.py
```

All tests verify:
- Accurate retrieval of REGA license #1200016591 from `wasalt.sa`.
- Accurate retrieval of DAR Group verticals (Naiza, DAR U, TNS+, Darlean) from `darglobal.com`.
- Rejection of out-of-scope questions without hallucination.
- Generation of structured citation metadata with clickable URLs.
- Bilingual RTL/LTR rendering.
