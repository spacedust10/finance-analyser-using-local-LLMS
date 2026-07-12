import json
import urllib.request

OLLAMA_URL = "http://localhost:11434"
EMBED_PREFIXES = ("nomic-embed-text", "mxbai-embed-large", "bge-m3", "snowflake-arctic-embed", "all-minilm")

def installed_models(timeout: float = 2.0) -> list:
    """Model names available in the local Ollama; [] when unreachable."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=timeout) as r:
            tags = json.load(r).get("models", [])
        return sorted(m["name"] for m in tags)
    except Exception:
        return []

def chat_models(models: list) -> list:
    """Models suitable for chat/classification (embedding-only models filtered out)."""
    generative = [m for m in models if not m.startswith(EMBED_PREFIXES)]
    return generative or models

def pick_embed_model(models: list, fallback: str) -> str:
    """Prefer a dedicated embedding model when one is installed."""
    for m in models:
        if m.startswith(EMBED_PREFIXES):
            return m
    return fallback
