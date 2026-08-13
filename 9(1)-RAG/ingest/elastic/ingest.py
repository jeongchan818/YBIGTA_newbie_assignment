"""Ingest corpus into Elasticsearch BM25 index (wiki-bm25).

Index mapping: text field only (no vectors).
Bulk chunk_size=500 (lightweight without vectors).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-bm25"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=60,
    )


def _generate_actions(corpus_path: Path):
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": {
                    "text": doc["text"],
                },
            }


def ingest(progress_callback=None):
    """Create BM25 index and bulk-ingest corpus into Elasticsearch.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Use get_es_client() to get ES client
        - Delete existing index if it exists, then create with INDEX_MAPPINGS
        - Corpus is at RAW_DIR / "corpus.jsonl"
        - Use _generate_actions(corpus_path) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=500
        - Call es.indices.refresh() after bulk ingest
    """
    corpus_path = RAW_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        raise FileNotFoundError(
            f"{corpus_path} 가 없습니다. 먼저 python data/download.py 를 실행하세요."
        )
 
    es = get_es_client()
 
    # 1) 기존 인덱스 삭제 후 재생성 (매번 깨끗한 상태에서 시작)
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    es.indices.create(index=INDEX_NAME, mappings=INDEX_MAPPINGS)
 
    # 2) bulk 적재
    actions = tqdm(
        _generate_actions(corpus_path),
        desc=f"Indexing to {INDEX_NAME}",
        unit="doc",
    )
    success, errors = bulk(es, actions, chunk_size=500, request_timeout=120)
 
    if errors:
        print(f"[경고] 실패한 문서 {len(errors)}건")
 
    # 3) refresh 해야 방금 넣은 문서가 검색에 잡힌다
    es.indices.refresh(index=INDEX_NAME)
 
    count = es.count(index=INDEX_NAME)["count"]
    print(f"{INDEX_NAME}: {count} docs indexed (bulk success={success})")
 
    if progress_callback:
        progress_callback(count)
 
    return count
    


if __name__ == "__main__":
    ingest()
