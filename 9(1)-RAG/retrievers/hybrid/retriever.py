"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN.

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    if not query or not query.strip():
        return []
 
    # 1) 쿼리 임베딩 (kNN 쪽에서 사용)
    vector = embed_query(query)
 
    es = get_es_client()
 
    # 2) BM25(standard) + kNN 두 검색기를 RRF로 융합
    response = es.search(
        index=INDEX_NAME,
        retriever={
            "rrf": {
                "retrievers": [
                    {
                        "standard": {
                            "query": {"match": {"text": query}}
                        }
                    },
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": vector,
                            "k": candidate_size,
                            "num_candidates": candidate_size * 2,
                        }
                    },
                ],
                "rank_constant": 60,
                "rank_window_size": candidate_size,
            }
        },
        size=top_k,
        source=["text"],  # 4096차원 embedding까지 받아오지 않도록 제외
    )
 
    # 3) 약속된 형식으로 변환
    results = []
    for hit in response["hits"]["hits"]:
        results.append(
            {
                "id": hit["_id"],
                "text": hit["_source"]["text"],
                "score": hit["_score"],
                "method": "Hybrid (RRF)",
            }
        )
    return results
 
