from pydantic import BaseModel
from typing import List
from features.openai_config import client
from config.pinecone import idx



class Subtopic(BaseModel):
    topic: str
    subtopics: List[str]

class TopicExtractionResponse(BaseModel):
    main_topics: List[Subtopic] 

def extract_all_topics(results: List[dict]) -> TopicExtractionResponse:
    """Extracts main topics and subtopics from all search results."""
    combined_texts = "\n".join(["\n".join(res["text"]) for res in results])

    prompt = f"""
    Extract main topics and subtopics from the following text:
    
    {combined_texts}
    must be specific and remain relevant to the text. don't include any irrelevant information.donot use any term or word that is extraneous to the text.
    use normal vocbulary. topics should be generalized enough to explain the text.
    
    Provide output in JSON format: {{"main_topics": [{{"topic": "...", "subtopics": ["...", "..."]}}]}}.
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Extract structured topics from documents."},
            {"role": "user", "content": prompt}
        ],
        response_format=TopicExtractionResponse,
    )

    return response.choices[0].message.parsed


class QuestionGenerationResponse(BaseModel):
    questions: list[str]


def generate_questions(main_topic: str, subtopic: str, context: str, num_questions: int = 5) -> QuestionGenerationResponse:
    """Generates questions based on a selected topic, subtopic, and context."""
    prompt = f"""
    Generate {num_questions} questions based on the following information:
    
    Main Topic: {main_topic}
    Subtopic: {subtopic}
    Context: {context}
    
    these qiestions are for educational purposes and should be relevant to the given information. and must be answerable from the given context.
    
    questions should be clear and concise.
    
    questions should be in a format that can be answered in a single sentence.
    questions should be lineant enough to be answered by a any mental level student.
    questions should be short and simple.
    
    Output questions as a JSON list: {{"questions": ["Q1", "Q2", ...]}}.
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Generate educational questions."},
            {"role": "user", "content": prompt}
        ],
        response_format=QuestionGenerationResponse,
    )

    return response.choices[0].message.parsed


def generate(subject, book):
    # Query using an equality filter for the 'title'
    results = idx.query(
        vector=[0.0] * 1536,
        namespace=subject,
        top_k=100,
        include_metadata=True,
        filter={"title": {"$eq": book}}  # Using equality operator for filtering
    )
    
    # Debug: print the entire query result to inspect its structure
    # print("Query Results:", results)
    
    output = []
    matches = results.get("matches")
    if not matches:
        print("No matches found for the provided filter.")
        return output
    
    for match in matches:
        metadata = match.get("metadata", {})
        meta_title = metadata.get("title", "")
        text = metadata.get("text", "")
        output.append({"title": meta_title, "text": text})
    
    return output
