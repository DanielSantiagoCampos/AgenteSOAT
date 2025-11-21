# src/retriever.py
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_DOCS

@dataclass
class DocumentChunk:
    doc_id: str
    chunk_id: int
    text: str
    source_path: Path

class KnowledgeBase:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.vectorizer = None
        self.tfidf_matrix = None

    def _load_pdf(self, path: Path) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                text += t + "\n"
        return text

    def _chunk_text(self, text: str, doc_id: str, source_path: Path) -> List[DocumentChunk]:
        chunks = []
        start = 0
        chunk_id = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append(
                    DocumentChunk(
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        text=chunk_text,
                        source_path=source_path,
                    )
                )
                chunk_id += 1
            start = end - CHUNK_OVERLAP
        return chunks

    def index_documents(self, docs_dir: Path = DOCS_DIR):
        self.chunks = []
        texts = []

        for filename in os.listdir(docs_dir):
            path = docs_dir / filename
            if not path.is_file():
                continue
            if path.suffix.lower() != ".pdf":
                continue

            try:
                text = self._load_pdf(path)
            except Exception as e:
                print(f"[WARN] No se pudo leer {filename}: {e}")
                continue

            doc_chunks = self._chunk_text(text, filename, path)
            self.chunks.extend(doc_chunks)

        if not self.chunks:
            print("[WARN] No hay chunks para indexar.")
            return

        texts = [c.text for c in self.chunks]
        # self.vectorizer = TfidfVectorizer(stop_words="spanish")
        self.vectorizer = TfidfVectorizer(stop_words=None)

        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        print(f"[INFO] Indexados {len(self.chunks)} chunks de documentación SOAT.")

    def retrieve(self, query: str, top_k: int = TOP_K_DOCS) -> List[Dict]:
        if self.vectorizer is None or self.tfidf_matrix is None:
            raise RuntimeError("La base de conocimiento no está indexada.")

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        indices = sims.argsort()[::-1][:top_k]

        results = []
        for idx in indices:
            c = self.chunks[idx]
            results.append(
                {
                    "doc_id": c.doc_id,
                    "chunk_id": c.chunk_id,
                    "score": float(sims[idx]),
                    "text": c.text,
                    "source_path": str(c.source_path),
                }
            )
        return results
