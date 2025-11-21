# src/config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
DATASETS_DIR = DATA_DIR / "datasets"

OUTPUT_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = OUTPUT_DIR / "logs"

# Modelo de Ollama que tengas descargado (ajusta si usas otro)
OLLAMA_MODEL = "llama3.1:8b"

# Parámetros de RAG
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
TOP_K_DOCS = 5
