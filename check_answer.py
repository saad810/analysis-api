from features.openai_config import client
from pydantic import BaseModel
from index_queries import search_similar_materials
from typing import List

class IncorrectFact(BaseModel):
    statement: str  # Example: "World War 1 did not happen in 1990"
    explanation: str  # Example: "World War 1 started in 1914 and ended in 1918."

class AnswerValidation(BaseModel):
    is_correct: bool
    score: float  # Confidence score between 0 and 1
    incorrect_facts: List[IncorrectFact]  # List of incorrect facts

def validate_answer(question: str, user_answer: str, subject: str, client) -> dict:
    # Retrieve context from Pinecone
    context = search_similar_materials(question, client, subject)

    if not context:
        return {"error": "No relevant context found for validation."}

    # Call OpenAI GPT-4o for validation, ensuring the response is automatically parsed as AnswerValidation
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": (
                    "Validate the user's answer based on the given context. "
                    "For each incorrect fact, correct it in the format: "
                    "'Statement: {corrected_fact}. Explanation: {correct information with reason}'. "
                    "Provide a score between 0 and 1."
                )
            },
            {
                "role": "user",
                "content": f"Question: {question}\nUser Answer: {user_answer}\nContext: {context}\n\nValidate the user's answer."
            }
        ],
        response_format=AnswerValidation  # This tells the client to parse the output accordingly
    )

    # Access the parsed response directly
    answer_validation = completion.choices[0].message.parsed

    # Convert to dictionary format for Flask
    return {
        "is_correct": answer_validation.is_correct,
        "score": answer_validation.score,
        "incorrect_facts": [
            {
                "statement": fact.statement,
                "explanation": fact.explanation
            } for fact in answer_validation.incorrect_facts
        ]
    }
