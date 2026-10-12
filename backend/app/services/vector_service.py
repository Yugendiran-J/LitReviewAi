import os
import json

import faiss
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


VECTOR_DIRECTORY = "documents/vector_indexes"

os.makedirs(
    VECTOR_DIRECTORY,
    exist_ok=True
)


def create_vector_index(
    project_id: int,
    paper_id: int,
    chunks: list[dict]
):

    if not chunks:
        raise ValueError(
            "No chunks available for vector indexing"
        )

    texts = [
        chunk["chunk_text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(embeddings)

    index_path = os.path.join(
        VECTOR_DIRECTORY,
        f"paper_{paper_id}.index"
    )

    metadata_path = os.path.join(
        VECTOR_DIRECTORY,
        f"paper_{paper_id}_metadata.json"
    )

    faiss.write_index(
        index,
        index_path
    )

    metadata = []

    for chunk in chunks:
        metadata.append({
            "chunk_id": chunk["id"],
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk["page_number"],
            "chunk_text": chunk["chunk_text"]
        })

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )

    return {
        "index_path": index_path,
        "metadata_path": metadata_path,
        "total_chunks": len(chunks),
        "embedding_dimension": dimension
    }


def search_vector_index(
    paper_id: int,
    query: str,
    top_k: int = 3
):

    index_path = os.path.join(
        VECTOR_DIRECTORY,
        f"paper_{paper_id}.index"
    )

    metadata_path = os.path.join(
        VECTOR_DIRECTORY,
        f"paper_{paper_id}_metadata.json"
    )

    if not os.path.exists(index_path):
        raise FileNotFoundError(
            "Vector index not found for this paper"
        )

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            "Vector metadata not found for this paper"
        )

    index = faiss.read_index(
        index_path
    )

    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    top_k = min(
        top_k,
        index.ntotal
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0]
    ):

        if index_position < 0:
            continue

        chunk = metadata[index_position]

        results.append({
            "chunk_id": chunk["chunk_id"],
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk["page_number"],
            "chunk_text": chunk["chunk_text"],
            "distance": float(distance)
        })

    return results