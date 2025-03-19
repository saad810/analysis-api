from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
# Import custom modules
from lib.grammar_check import grammar_check
from lib.check_answer import validate_answer
from lib.generate_questions import generate, extract_all_topics, generate_questions
from config.openai import client

# Initialize FastAPI app
app = FastAPI(title="Text Analysis API",
              description="APIs for grammar checking, answer validation, and question generation.",
              docs_url="/docs")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GrammarCheckRequest(BaseModel):
    text: str

class GrammarCheckResponse(BaseModel):
    results: List[dict]

class AnswerValidationRequest(BaseModel):
    question: str
    user_answer: str
    subject: str

class IncorrectFact(BaseModel):
    statement: str
    explanation: str

class AnswerValidationResponse(BaseModel):
    is_correct: bool
    score: float
    incorrect_facts: List[IncorrectFact]

class GenerationRequest(BaseModel):
    book: str
    subject: str
    num_questions: int = 5
    type: str = "text_based"

class GenerationResponse(BaseModel):
    questions: List[str]

# Endpoints
@app.post("/grammar/check", response_model=GrammarCheckResponse)
def check_grammar(request: GrammarCheckRequest):
    try:
        print(request.text)
        results = grammar_check(request.text)
        return {"results": [r.dict() for r in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer/analyze", response_model=AnswerValidationResponse)
def analyze_answer(request: AnswerValidationRequest):
    try:
        return validate_answer(request.question, request.user_answer, request.subject, client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/questions", response_model=GenerationResponse)
def generate_questions_api(request: GenerationRequest):
    try:
        results = generate(book=request.book, subject=request.subject)
        if not results:
            raise HTTPException(status_code=400, detail="No text generated.")
        
        topics = extract_all_topics(results)
        combined_texts = "\n".join("\n".join(res["text"]) for res in results)
        main_topics = [sub.topic for sub in topics.main_topics]
        
        if len(main_topics) < 2:
            raise HTTPException(status_code=400, detail="Not enough topics extracted.")
        
        questions_response = generate_questions(
            main_topic=main_topics[0],
            subtopic=main_topics[1],
            context=combined_texts,
            question_type=request.type,
            num_questions=request.num_questions
        )
        
        return {"questions": [q.dict() if hasattr(q, "dict") else str(q) for q in questions_response.questions]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app (only for local testing, use Uvicorn to run in production)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
