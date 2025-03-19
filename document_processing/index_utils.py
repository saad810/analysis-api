import re
from docs import process_text
from langdetect import detect
from constants import EMBEDDINGS_MODEL
from langchain_text_splitters import RecursiveCharacterTextSplitter




def get_embeddings(data, openai_client):
    # Generate embeddings

    response = openai_client.embeddings.create(
        model=EMBEDDINGS_MODEL,
        input = data,
    )
    return response.data[0].embedding
    # return response
    # return response

    
def process_chunking_docs(string: str, chunk_size: int = 2000, chunk_overlap: int = 500) -> list:
    print("""Splits text into chunks for processing.""")    
    # print(string)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_text(string)  
    return texts
    

def generate_embeddings(file_path, openai_client):
    text = process_text(file_path)
    if text is None:
        return "Error processing text"
    
    print("Text processed")
    chunks = process_chunking_docs(text)
    if len(chunks) == 0:
        return "No sentences found"
    print("Sentences split")
    embeddings_data = []
    # print(embeddings(text))
    for chunk in chunks:
        response = get_embeddings(chunk, openai_client)

        
        embeddings_data.append({
            'text': chunks,
            'embedding': response
        })
    
    print("Embeddings generated")
    if len(embeddings_data) == 0:
        return "No embeddings Found"
    return embeddings_data


