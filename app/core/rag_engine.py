"""RAG Engine: Embeds knowledge base documents and provides forensic Q&A retrieval."""

import os
import re
import hashlib
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

KB_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma_db"
COLLECTION_NAME = "forensics_kb"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def _chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks with metadata."""
    paragraphs = re.split(r"\n{2,}", text)
    chunks, current, start = [], "", 0
    for para in paragraphs:
        if len(current) + len(para) > CHUNK_SIZE and current:
            chunks.append({"text": current.strip(), "source": source, "index": start})
            # keep overlap
            words = current.split()
            overlap_words = words[-CHUNK_OVERLAP // 5 :] if len(words) > CHUNK_OVERLAP // 5 else words
            current = " ".join(overlap_words) + "\n\n" + para
            start += 1
        else:
            current += "\n\n" + para if current else para
    if current.strip():
        chunks.append({"text": current.strip(), "source": source, "index": start})
    return chunks


def _file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


class RAGEngine:
    def __init__(self):
        self.model = None
        self.client = None
        self.collection = None
        self._loaded = False

    def initialize(self):
        if self._loaded:
            return
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._loaded = True

    def index_knowledge_base(self, force: bool = False) -> int:
        """Index all markdown files from the knowledge base. Returns chunk count."""
        self.initialize()
        if self.collection.count() > 0 and not force:
            return self.collection.count()

        # Clear existing
        if self.collection.count() > 0:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

        all_chunks = []
        for md_file in sorted(KB_DIR.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            chunks = _chunk_text(text, md_file.name)
            all_chunks.extend(chunks)

        # Also index extracted text files if available
        extracted_dir = KB_DIR.parent / "extracted"
        if extracted_dir.exists():
            for txt_file in sorted(extracted_dir.glob("*.txt")):
                text = txt_file.read_text(encoding="utf-8")
                chunks = _chunk_text(text, f"extracted/{txt_file.name}")
                all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        # Batch embed and add
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            texts = [c["text"] for c in batch]
            embeddings = self.model.encode(texts).tolist()
            ids = [f"chunk_{i + j}" for j in range(len(batch))]
            metadatas = [{"source": c["source"], "index": c["index"]} for c in batch]
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

        return len(all_chunks)

    def query(self, question: str, n_results: int = 8) -> list[dict]:
        """Query the knowledge base and return relevant chunks."""
        self.initialize()
        if self.collection.count() == 0:
            self.index_knowledge_base()

        q_embedding = self.model.encode([question]).tolist()
        results = self.collection.query(
            query_embeddings=q_embedding,
            n_results=min(n_results, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "text": doc,
                "source": meta["source"],
                "relevance": round(1 - dist, 3),
            })
        return output

    def get_context_for_prompt(self, question: str, n_results: int = 8) -> str:
        """Get formatted context string for LLM prompt construction."""
        results = self.query(question, n_results)
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"--- Source: {r['source']} (relevance: {r['relevance']}) ---\n{r['text']}"
            )
        return "\n\n".join(context_parts)
