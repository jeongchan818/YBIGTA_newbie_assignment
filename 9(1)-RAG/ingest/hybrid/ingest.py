"""Ingest corpus into Elasticsearch Hybrid index (wiki-hybrid).

Index mapping: text field + dense_vector(4096, cosine).
Bulk chunk_size=100 (heavier with 4096-dim vectors).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-hybrid"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
        "embedding": {
            "type": "dense_vector",
            "dims": 4096,
            "index": True,
            "similarity": "cosine",
        },
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=120,
    )


def _generate_actions(corpus_path: Path, embeddings: np.ndarray, ids: list[str]):
    id_to_idx = {doc_id: idx for idx, doc_id in enumerate(ids)}

    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            doc_id = doc["id"]
            idx = id_to_idx.get(doc_id)
            if idx is None:
                continue
            yield {
                "_index": INDEX_NAME,
                "_id": doc_id,
                "_source": {
                    "text": doc["text"],
                    "embedding": embeddings[idx].tolist(),
                },
            }


def ingest(progress_callback=None):
    """Create hybrid index (text + dense_vector) and bulk-ingest corpus.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Use get_es_client(), delete/create index with INDEX_MAPPINGS
        - Use _generate_actions(corpus_path, embeddings, ids) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=100
        - Call es.indices.refresh() after bulk ingest
    """
    corpus_path = RAW_DIR / "corpus.jsonl"
    emb_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
 
    for p in (corpus_path, emb_path, ids_path):
        if not p.exists():
            raise FileNotFoundError(f"{p} 가 없습니다. 이전 단계를 먼저 실행하세요.")
 
    # 1) 임베딩과 ID 로드
    embeddings = np.load(emb_path)
    ids = json.loads(ids_path.read_text(encoding="utf-8"))
 
    if len(ids) != embeddings.shape[0]:
        raise ValueError(f"ids({len(ids)})와 embeddings({embeddings.shape[0]}) 개수가 다릅니다.")
 
    es = get_es_client()
 
    # 2) 기존 인덱스 삭제 후 매핑과 함께 재생성
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    es.indices.create(index=INDEX_NAME, mappings=INDEX_MAPPINGS)
 
    # 3) bulk 적재 (벡터가 붙어 무거우므로 chunk_size=100)
    actions = tqdm(
        _generate_actions(corpus_path, embeddings, ids),
        desc=f"Indexing to {INDEX_NAME}",
        unit="doc",
        total=len(ids),
    )
    success, errors = bulk(es, actions, chunk_size=100, request_timeout=300)
 
    if errors:
        print(f"[경고] 실패한 문서 {len(errors)}건")
 
    # 4) refresh 후 개수 확인
    es.indices.refresh(index=INDEX_NAME)
    count = es.count(index=INDEX_NAME)["count"]
    print(f"{INDEX_NAME}: {count} docs indexed (bulk success={success})")
 
    if progress_callback:
        progress_callback(count)
 
    return count


if __name__ == "__main__":
    ingest()
