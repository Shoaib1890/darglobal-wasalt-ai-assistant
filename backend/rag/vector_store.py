import os
import json
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from backend.config import CHROMA_PERSIST_DIR, RAG_CHUNKS_PATH
from backend.rag.embedder import embedder

logger = logging.getLogger(__name__)

COLLECTION_NAME = "dar_wasalt_knowledge"

class VectorStoreManager:
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        logger.info(f"Initializing ChromaDB client at: {self.persist_dir}")
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        self._ensure_indexed()

    def _ensure_indexed(self):
        """Checks if verified chunks are indexed into ChromaDB. Indexes if empty or updated."""
        if not os.path.exists(RAG_CHUNKS_PATH):
            logger.warning(f"RAG chunks file not found at: {RAG_CHUNKS_PATH}")
            return

        with open(RAG_CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        existing_count = self.collection.count()
        logger.info(f"ChromaDB collection count: {existing_count}, Target chunks: {len(chunks)}")

        if existing_count < len(chunks):
            logger.info(f"Indexing {len(chunks)} verified chunks into ChromaDB...")
            ids = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                ids.append(chunk["chunk_id"])
                # Combine section, metadata keywords and text for rich bilingual indexing
                meta_keywords = " ".join(str(v) for v in chunk.get("metadata", {}).values() if isinstance(v, (str, int)))
                enriched_text = f"{chunk['domain']} {chunk['section']} {meta_keywords}\n{chunk['text']}"
                documents.append(enriched_text)
                # Store metadata for retrieval and attribution
                meta = {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "domain": chunk["domain"],
                    "source_url": chunk["source_url"],
                    "page_title": chunk["page_title"][:100],
                    "section": chunk["section"][:100],
                    "language": chunk["language"]
                }
                metadatas.append(meta)

            # Generate embeddings
            embeddings = embedder.encode(documents).tolist()

            # Batch upsert into Chroma
            batch_size = 50
            for i in range(0, len(ids), batch_size):
                self.collection.upsert(
                    ids=ids[i:i + batch_size],
                    embeddings=embeddings[i:i + batch_size],
                    documents=documents[i:i + batch_size],
                    metadatas=metadatas[i:i + batch_size]
                )
            logger.info("ChromaDB index populated successfully.")

    def query(
        self, 
        query_text: str, 
        n_results: int = 4, 
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries the vector database using cosine semantic similarity."""
        query_embedding = embedder.encode(query_text).tolist()
        
        where_filter = None
        if domain_filter:
            where_filter = {"domain": domain_filter}

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                # Cosine distance in Chroma: score = 1.0 - distance
                distance = results["distances"][0][i]
                similarity_score = max(0.0, min(1.0, 1.0 - distance))
                meta = results["metadatas"][0][i]
                text = results["documents"][0][i]
                
                formatted_results.append({
                    "chunk_id": results["ids"][0][i],
                    "doc_id": meta.get("doc_id", ""),
                    "domain": meta.get("domain", ""),
                    "source_url": meta.get("source_url", ""),
                    "page_title": meta.get("page_title", ""),
                    "section": meta.get("section", ""),
                    "language": meta.get("language", ""),
                    "text": text,
                    "score": similarity_score,
                    "metadata": meta
                })

        return formatted_results

    def get_count(self) -> int:
        return self.collection.count()

vector_store = VectorStoreManager()
