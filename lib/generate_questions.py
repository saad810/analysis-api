from config.openai import client
from models.schema_models import TopicExtractionResponse,QuestionGenerationResponse
from config.pinecone import idx
from typing import List
from constants import QuestionType


def extract_all_topics(results: List[dict]) -> TopicExtractionResponse:
    """Extracts main topics and subtopics from all search results."""
    combined_texts = "\n".join(["\n".join(res["text"]) for res in results])
    
    prompt = f"""
    Extract main topics and subtopics from the following text:
    {combined_texts}
    Must be specific and remain relevant to the text. Don't include any irrelevant information.
    Use normal vocabulary. Topics should be generalized enough to explain the text.
    
    Provide output in JSON format: {"{"}main_topics": [{{"topic": "...", "subtopics": ["...", "..."]}}]. 
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

# Define allowed question types


def generate_questions(main_topic: str, subtopic: str, context: str, question_type: QuestionType, num_questions: int = 5) -> QuestionGenerationResponse:
    """Generates questions of a specified type based on a selected topic, subtopic, and context."""
    prompt = f"""
    Generate {num_questions} {question_type} questions based on the following information:
    
    Main Topic: {main_topic}
    Subtopic: {subtopic}
    Context: {context}
    
    These questions are for educational purposes and should be relevant to the given information.
    - Questions should be clear and concise.
    - If multiple-choice, provide four options and specify the correct answer.
    - If true/false, provide a statement and indicate if it's true or false.
    - If fill-in-the-blank, create a sentence with a missing word and provide the answer.
    - If text-based, create a short-answer question.
    
    Provide output in JSON format: {"{"}questions": [{{"type": "{question_type}", "question": "...", "options": ["A", "B", "C", "D"], "answer": "..."}}].
     
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

def generate(subject: str, book: str):
    """Fetches text from the database based on subject and book title."""
    results = idx.query(
        vector=[0.0] * 1536,
        namespace=subject,
        top_k=100,
        include_metadata=True,
        filter={"title": {"$eq": book}}
    )
    
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
