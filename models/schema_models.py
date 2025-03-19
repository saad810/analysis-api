from typing import List, Union
from pydantic import BaseModel
from constants import QuestionType

class GrammarModel(BaseModel):
    sentence: str
    corrected_sentence: str
    errors: List[str]  # Explicitly specify list items as strings


class IncorrectFact(BaseModel):
    statement: str  # Example: "World War 1 did not happen in 1990"
    explanation: str  # Example: "World War 1 started in 1914 and ended in 1918."

class AnswerValidation(BaseModel):
    is_correct: bool
    score: float  # Confidence score between 0 and 1
    incorrect_facts: List[IncorrectFact]  # List of incorrect facts

class Subtopic(BaseModel):
    topic: str
    subtopics: List[str]

class TopicExtractionResponse(BaseModel):
    main_topics: List[Subtopic]

class Question(BaseModel):
    type: QuestionType
    question: str
    options: Union[List[str], None] = None  # Only for MCQs
    answer: str  # Correct answer

class QuestionGenerationResponse(BaseModel):
    questions: List[Question]