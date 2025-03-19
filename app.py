from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from pydantic import BaseModel
from features.grammar import grammar_check  # Grammar check function
from check_answer import validate_answer  # Answer validation function
from features.openai_config import client
from flask_cors import CORS
# Import your generation functions:
from generate_questions import generate, extract_all_topics, generate_questions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  

# Enable Swagger UI at /docs
api = Api(
    app, 
    title="Text Analysis API", 
    description="APIs for grammar checking, answer validation, and question generation.", 
    doc="/docs"  # Swagger UI endpoint
)

### ====== Grammar Checking API ====== ###
grammar_ns = api.namespace("grammar", description="Grammar Checking API")

grammar_model = api.model(
    "GrammarCheckRequest",
    {"text": fields.String(required=True, description="Text to check for grammar issues")}
)

grammar_response_model = api.model(
    "GrammarCheckResponse",
    {"results": fields.List(fields.Raw, description="List of grammar issues found")}
)

@grammar_ns.route("/check")
class GrammarCheckResource(Resource):
    @api.expect(grammar_model)
    @api.response(200, "Success", grammar_response_model)
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        """Checks grammar for the given text"""
        data = request.get_json()
        if not data or "text" not in data:
            return {"error": "No text provided"}, 400
        text = data["text"]
        try:
            results = grammar_check(text)
            serialized_results = [r.dict() for r in results]
            return {"results": serialized_results}, 200
        except Exception as e:
            return {"error": str(e)}, 500

### ====== Answer Validation API ====== ###
answer_ns = api.namespace("answer", description="Answer Validation API")

answer_model = api.model(
    "AnswerValidationRequest",
    {
        "question": fields.String(required=True, description="Question asked"),
        "user_answer": fields.String(required=True, description="User's answer"),
        "subject": fields.String(required=True, description="Subject area for context retrieval")
    }
)

incorrect_fact_model = api.model(
    "IncorrectFact",
    {
        "statement": fields.String(description="Incorrect fact with corrected statement"),
        "explanation": fields.String(description="Explanation of why the fact is incorrect")
    }
)

answer_response_model = api.model(
    "AnswerValidationResponse",
    {
        "is_correct": fields.Boolean(description="Whether the answer is factually correct"),
        "score": fields.Float(description="Confidence score between 0 and 1"),
        "incorrect_facts": fields.List(fields.Nested(incorrect_fact_model), description="List of incorrect facts found")
    }
)

@answer_ns.route("/analyze")
class AnswerValidationResource(Resource):
    @api.expect(answer_model)
    @api.response(200, "Success", answer_response_model)
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        """Analyzes the answer for factual accuracy"""
        data = request.get_json()
        if not data or "question" not in data or "user_answer" not in data or "subject" not in data:
            return {"error": "Missing required fields"}, 400

        question = data["question"]
        user_answer = data["user_answer"]
        subject = data["subject"]

        try:
            result = validate_answer(question, user_answer, subject, client)
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500

### ====== Question Generation API ====== ###
generation_ns = api.namespace("generate", description="Question Generation API")

# Request model for question generation
generation_request_model = api.model(
    "GenerationRequest",
    {
        "book": fields.String(required=True, description="Book or text title"),
        "subject": fields.String(required=True, description="Subject area"),
        "num_questions": fields.Integer(required=False, default=5, description="Number of questions to generate"),
        "type": fields.String(required=False, default="text_based", description="Type of questions to generate")
    }
)

# Response model for question generation
generation_response_model = api.model(
    "GenerationResponse",
    {
        "questions": fields.List(fields.String, description="List of generated questions")
    }
)

@generation_ns.route("/questions")
class QuestionGenerationResource(Resource):
    @api.expect(generation_request_model)
    @api.response(200, "Success", generation_response_model)
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        """Generates questions based on the provided book and subject"""
        data = request.get_json()
        book = data.get("book")
        subject = data.get("subject")
        question_type = data.get("type", "text_based")  # Default to text-based
        num_questions = data.get("num_questions", 5)
        
        # Generate text results
        results = generate(
            book=book,
            subject=subject,
        )
        if not results:
            return {"error": "No text generated."}, 400

        # Extract topics and combine text for context
        topics = extract_all_topics(results)
        combined_texts = "\n".join(["\n".join(res["text"]) for res in results])
        
        # Access main topics from the TopicExtractionResponse object
        main_topic_names = [sub.topic for sub in topics.main_topics]
        
        if len(main_topic_names) < 2:
            return {"error": "Not enough topics extracted."}, 400
        
        # Generate questions using the first two main topics and the combined texts as context
        questions_response = generate_questions(
            main_topic=main_topic_names[0],
            subtopic=main_topic_names[1],
            context=combined_texts,
            question_type=question_type,
            num_questions=num_questions
            
        )
        # questions_list = questions_response.questions
        
        # return {"questions": questions_list}, 200
        questions_list = [q.dict() if hasattr(q, "dict") else str(q) for q in questions_response.questions]
        return {"questions": questions_list}, 200

# Add namespaces to API
api.add_namespace(grammar_ns)
api.add_namespace(answer_ns)
api.add_namespace(generation_ns)

if __name__ == '__main__':
    app.run(debug=True)
