import logging
from index_utils import get_embeddings  # Ensure this generates a single embedding for queries
from config.pinecone import idx  # Use the existing Pinecone index

def search_similar_materials(query_text, client, subject, top_k=5, threshold=0.45):
    try:
        # Generate embedding for the query
        query_embedding = get_embeddings(data=query_text, openai_client=client)

        if not query_embedding:
            logging.error("Failed to generate embedding for query.")
            return []

        # Perform similarity search
        search_results = idx.query(
            vector=query_embedding,
            namespace=subject,
            top_k=top_k,
            include_values=True,  # ✅ Include vector values instead of text
            include_metadata=True  
        )

        # Process results with threshold filtering
        matches = [
            {
                "title": match["metadata"]["title"],
                "score": match["score"],
                # "vector": match["values"]  # ✅ Extract vector for context
                "text": match["metadata"].get("text", "No text available")  # ✅ Extract stored text
            }
            for match in search_results["matches"] if match["score"] >= threshold  # ✅ Apply threshold
        ]

        return matches

    except Exception as e:
        logging.error(f"Error in similarity search: {e}")
        return []

def get_all_subjects():
    stats = idx.describe_index_stats()
    # The 'namespaces' key is a dictionary with namespace names as keys
    namespaces = list(stats.get("namespaces", {}).keys())
    return namespaces

def get_all_titles_in_subject(subject: str, dimension: int = 1536, top_k: int = 1000):
    """
    Retrieve unique document titles stored in a specific namespace (subject).

    This function queries Pinecone using a dummy vector and extracts the title from each document's metadata.
    It then returns a list of unique titles (preserving the original order).
    """
    # Create a dummy vector of zeros with the specified dimension
    dummy_vector = [0.0] * dimension

    results = idx.query(
        vector=dummy_vector,
        namespace=subject,
        top_k=top_k,
        include_metadata=True
    )

    # Use a set to track seen titles and a list to preserve order
    seen = set()
    unique_titles = []
    for match in results.get("matches", []):
        title = match.get("metadata", {}).get("title", "Unknown Title")
        if title not in seen:
            seen.add(title)
            unique_titles.append(title)
    return unique_titles
