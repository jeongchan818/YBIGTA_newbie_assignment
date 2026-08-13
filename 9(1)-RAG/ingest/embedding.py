"""Upstage Solar embedding utility with disk caching and parallel API keys.

Models:
  - solar-embedding-1-large-passage  (document encoding)
  - solar-embedding-1-large-query    (query encoding)

Uses multiple API keys (UPSTAGE_API_KEY1..N) for parallel embedding.
Each key gets its own thread with independent RPM/TPM limits.
Saves progress incrementally so crashes don't lose work.
Cache: data/processed/embeddings.npy (float32) + embedding_ids.json
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"

BATCH_SIZE = 100
RPM_LIMIT = 100
MIN_INTERVAL = 60.0 / RPM_LIMIT
DIM = 4096
BASE_URL = "https://api.upstage.ai/v1/solar"
MAX_CHARS = 12000  # ~3000 tokens, safely under 4000 token limit
MAX_RETRIES = 3


def _get_api_keys() -> list[str]:
    """Collect all UPSTAGE_API_KEY* from env."""
    keys = []
    for i in range(1, 100):
        key = os.getenv(f"UPSTAGE_API_KEY{i}")
        if key:
            keys.append(key.strip())
        else:
            break
    if not keys:
        single = os.getenv("UPSTAGE_API_KEY", "")
        if single:
            keys.append(single.strip())
    return keys


def _truncate(text: str) -> str:
    """Truncate text to stay within token limits."""
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS]
    return text


def _embed_batch_safe(client: OpenAI, batch: list[str]) -> list[list[float]]:
    """Embed a batch with retry and fallback to smaller sub-batches."""
    truncated = [_truncate(t) for t in batch]

    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model="solar-embedding-1-large-passage",
                input=truncated,
            )
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            err_msg = str(e)
            if "maximum context length" in err_msg or "4000 tokens" in err_msg:
                # Split batch in half and process separately
                mid = len(truncated) // 2
                if mid == 0:
                    # Single text too long, truncate more aggressively
                    truncated = [t[:MAX_CHARS // 2] for t in truncated]
                    continue
                left = _embed_batch_safe(client, truncated[:mid])
                time.sleep(MIN_INTERVAL)
                right = _embed_batch_safe(client, truncated[mid:])
                return left + right
            elif attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                raise

def _get_client() -> OpenAI:
    """Create an Upstage client (OpenAI-compatible)."""
    keys = _get_api_keys()
    if not keys:
        raise RuntimeError("Upstage API key가 없습니다. .env를 확인하세요.")
    return OpenAI(api_key=keys[0], base_url=BASE_URL)

def embed_passages(texts: list[str], ids: list[str], progress_callback=None) -> np.ndarray:
    """Embed passages using parallel API keys.

    Args:
        texts: List of passage strings to embed.
        ids: List of document IDs (same length as texts).
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        np.ndarray of shape (N, 4096), dtype float32.

    Hints:
        - Use _get_api_keys() to get API keys, OpenAI(api_key=..., base_url=BASE_URL) to create clients
        - Use _embed_batch_safe(client, batch) to embed a batch of texts
        - Process texts in chunks of BATCH_SIZE
        - Save results to EMBEDDINGS_PATH (.npy) and IDS_PATH (.json)
    """
    if len(texts) != len(ids):
        raise ValueError(f"texts({len(texts)})와 ids({len(ids)})의 길이가 다릅니다.")
 
    # 이미 같은 문서로 임베딩한 결과가 있으면 재사용 (API 재호출 방지)
    cached = load_cached_embeddings()
    if cached is not None and cached[1] == ids:
        print(f"캐시 사용: {EMBEDDINGS_PATH} {cached[0].shape}")
        return cached[0]
 
    client = _get_client()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
 
    total = len(texts)
    all_vectors: list[list[float]] = []
 
    for start in tqdm(range(0, total, BATCH_SIZE), desc="Embedding passages", unit="batch"):
        batch = texts[start:start + BATCH_SIZE]
 
        t0 = time.time()
        all_vectors.extend(_embed_batch_safe(client, batch))
 
        if progress_callback:
            progress_callback(len(all_vectors), total)
 
        # RPM 제한 준수
        elapsed = time.time() - t0
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
 
    embeddings = np.asarray(all_vectors, dtype=np.float32)
 
    if embeddings.shape != (total, DIM):
        raise RuntimeError(f"임베딩 shape 이상: {embeddings.shape}, 기대값 ({total}, {DIM})")
 
    np.save(EMBEDDINGS_PATH, embeddings)
    IDS_PATH.write_text(json.dumps(ids, ensure_ascii=False), encoding="utf-8")
 
    print(f"saved {embeddings.shape} -> {EMBEDDINGS_PATH}")
    return embeddings
 
 
_query_client: OpenAI | None = None


def embed_query(query: str) -> list[float]:
    """Embed a single query using the query model.

    Args:
        query: The search query string.

    Returns:
        list[float] of length 4096 (embedding vector).

    Hints:
        - Use _get_api_keys() to get an API key
        - Model name: "solar-embedding-1-large-query"
        - Use _truncate() to handle long queries
    """
    global _query_client
    if _query_client is None:
        _query_client = _get_client()
 
    response = _query_client.embeddings.create(
        model="solar-embedding-1-large-query",  # passage 모델과 다름에 주의
        input=_truncate(query),
    )
    return response.data[0].embedding
 
    
def load_cached_embeddings() -> tuple[np.ndarray, list[str]] | None:
    """Load cached embeddings from disk. Returns (embeddings, ids) or None."""
    if EMBEDDINGS_PATH.exists() and IDS_PATH.exists():
        embeddings = np.load(EMBEDDINGS_PATH)
        ids = json.loads(IDS_PATH.read_text())
        return embeddings, ids
    return None


if __name__ == "__main__":
    from data.download import RAW_DIR

    corpus_path = RAW_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        print("Run data/download.py first.")
        raise SystemExit(1)

    texts, ids = [], []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            ids.append(doc["id"])
            texts.append(doc["text"])

    embed_passages(texts, ids)
