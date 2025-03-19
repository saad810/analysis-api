
import logging
from document_processing.docs import get_pdf_metadata, get_file_extension, get_file_name
from index_utils import generate_embeddings
from dotenv import load_dotenv
from config.pinecone import idx
load_dotenv()


def store_pdf_in_pinecone(file_path, client,subject):
    try:
        file_metadata = get_pdf_metadata(file_path)
        extension = get_file_extension(file_path)
        title = file_metadata.get('title') or get_file_name(file_path)

        metadata = {
            "title": title,
            "subject": subject,
            "format": extension,
            "type": extension, 
            "difficulty": "unknown",  
            "extension": extension
        }

        # Generate embeddings (Extracted text included)
        embeddings_data = generate_embeddings(file_path=file_path, openai_client=client)

        if not embeddings_data:
            logging.error("No embeddings to insert into Pinecone")
            return

        # Prepare data for Pinecone
        vectors = [
            (f"{title}_{i}", item['embedding'], {**metadata, "text": item['text']})  # ✅ Include text chunk
            for i, item in enumerate(embeddings_data)
        ]
        # print(vectors)

        # Upsert into Pinecone (with namespace as Subject)
        idx.upsert(vectors=vectors, namespace=subject)
        
        print(f"Material '{title}' inserted successfully into Pinecone under '{subject}' namespace.")

        logging.info(f"Material '{title}' inserted successfully into Pinecone under '{subject}' namespace.")

    except Exception as e:
        logging.error(f"Error storing PDF in Pinecone: {e}")