"""Ingest embeddings into Pinecone vector index.

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

BATCH_SIZE = 100
TEXT_LIMIT = 1000  # metadata text truncation


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    emb_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    corpus_path = RAW_DIR / "corpus.jsonl"
 
    for p in (emb_path, ids_path, corpus_path):
        if not p.exists():
            raise FileNotFoundError(f"{p} 가 없습니다. 임베딩 단계를 먼저 실행하세요.")
 
    # 1) 임베딩과 ID 로드
    embeddings = np.load(emb_path)
    ids = json.loads(ids_path.read_text(encoding="utf-8"))
 
    if len(ids) != embeddings.shape[0]:
        raise ValueError(f"ids({len(ids)})와 embeddings({embeddings.shape[0]}) 개수가 다릅니다.")
 
    # 2) metadata용 원문 텍스트 로드 (id -> text)
    id_to_text = {}
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            id_to_text[doc["id"]] = doc["text"]
 
    # 3) Pinecone 연결
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX", "ragsession")
    index = pc.Index(index_name)
 
    # 4) 배치 upsert
    total = len(ids)
    for start in tqdm(range(0, total, BATCH_SIZE), desc=f"Upserting to {index_name}", unit="batch"):
        end = min(start + BATCH_SIZE, total)
 
        vectors = [
            {
                "id": ids[i],
                "values": embeddings[i].tolist(),
                "metadata": {"text": id_to_text.get(ids[i], "")[:TEXT_LIMIT]},
            }
            for i in range(start, end)
        ]
        index.upsert(vectors=vectors, namespace="__default__")
 
        if progress_callback:
            progress_callback(end, total)
 
    stats = index.describe_index_stats()
    print(f"{index_name}: {total} vectors upserted (index stats: {stats.get('total_vector_count')})")
 
    return total

if __name__ == "__main__":
    ingest()
