"""Vector retriever using Pinecone (cosine similarity)."""

import os

from dotenv import load_dotenv
from pinecone import Pinecone

from ingest.embedding import embed_query

load_dotenv()


def search(query: str, top_k: int = 10) -> list[dict]:
    """Vector cosine similarity search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Vector".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Use index.query(vector=..., top_k=..., include_metadata=True)
        - Text is in match["metadata"]["text"]
    """

    if not query or not query.strip():
        return []
 
    # 1) 쿼리를 query 전용 모델로 임베딩
    vector = embed_query(query)
 
    # 2) Pinecone 연결 후 코사인 유사도 상위 top_k 조회
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX", "ragsession"))
 
    response = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        namespace="__default__",
    )
 
    # 3) 약속된 형식으로 변환
    results = []
    for match in response["matches"]:
        results.append(
            {
                "id": match["id"],
                "text": match.get("metadata", {}).get("text", ""),
                "score": match["score"],
                "method": "Vector",
            }
        )
    return results
 
