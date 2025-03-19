from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS

# Import custom modules
from lib.grammar_check import grammar_check
from lib.check_answer import validate_answer
from lib.generate_questions import generate, extract_all_topics, generate_questions
from config.openai import client

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Enable Swagger UI at /docs
api = Api(
    app,
    title="Text Analysis API",
    description="APIs for grammar checking, answer validation, and question generation.",
    doc="/docs"
)

# Define API namespaces
grammar_ns = api.namespace("grammar", description="Grammar Checking API")
answer_ns = api.namespace("answer", description="Answer Validation API")
generation_ns = api.namespace("generate", description="Question Generation API")

# Define request/response models
grammar_model = api.model("GrammarCheckRequest", {"text": fields.String(required=True, description="Text to check for grammar issues")})
grammar_response_model = api.model("GrammarCheckResponse", {"results": fields.List(fields.Raw, description="List of grammar issues found")})

answer_model = api.model("AnswerValidationRequest", {
    "question": fields.String(required=True, description="Question asked"),
    "user_answer": fields.String(required=True, description="User's answer"),
    "subject": fields.String(required=True, description="Subject area for context retrieval")
})

incorrect_fact_model = api.model("IncorrectFact", {
    "statement": fields.String(description="Incorrect fact with corrected statement"),
    "explanation": fields.String(description="Explanation of why the fact is incorrect")
})

answer_response_model = api.model("AnswerValidationResponse", {
    "is_correct": fields.Boolean(description="Whether the answer is factually correct"),
    "score": fields.Float(description="Confidence score between 0 and 1"),
    "incorrect_facts": fields.List(fields.Nested(incorrect_fact_model), description="List of incorrect facts found")
})

generation_request_model = api.model("GenerationRequest", {
    "book": fields.String(required=True, description="Book or text title"),
    "subject": fields.String(required=True, description="Subject area"),
    "num_questions": fields.Integer(required=False, default=5, description="Number of questions to generate"),
    "type": fields.String(required=False, default="text_based", description="Type of questions to generate")
})

generation_response_model = api.model("GenerationResponse", {
    "questions": fields.List(fields.String, description="List of generated questions")
})

# API Endpoints
@grammar_ns.route("/check")
class GrammarCheckResource(Resource):
    @api.expect(grammar_model)
    @api.response(200, "Success", grammar_response_model)
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        data = request.get_json()
        if not data or "text" not in data:
            return {"error": "No text provided"}, 400
        try:
            results = grammar_check(data["text"])
            return {"results": [r.dict() for r in results]}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@answer_ns.route("/analyze")
class AnswerValidationResource(Resource):
    @api.expect(answer_model)
    @api.response(200, "Success", answer_response_model)
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        data = request.get_json()
        if not all(k in data for k in ("question", "user_answer", "subject")):
            return {"error": "Missing required fields"}, 400
        try:
            return validate_answer(data["question"], data["user_answer"], data["subject"], client), 200
        except Exception as e:
            return {"error": str(e)}, 500

@generation_ns.route("/questions")
class QuestionGenerationResource(Resource):
    @api.expect(generation_request_model)
    @api.response(200, "Success", generation_response_model)
    @api.response(400, "Bad Request")
    @api.response(500, "Internal Server Error")
    def post(self):
        data = request.get_json()
        book, subject = data.get("book"), data.get("subject")
        question_type, num_questions = data.get("type", "text_based"), data.get("num_questions", 5)
        
        results = generate(book=book, subject=subject)
        if not results:
            return {"error": "No text generated."}, 400
        
        topics = extract_all_topics(results)
        combined_texts = "\n".join("\n".join(res["text"]) for res in results)
        main_topics = [sub.topic for sub in topics.main_topics]
        
        if len(main_topics) < 2:
            return {"error": "Not enough topics extracted."}, 400
        
        questions_response = generate_questions(
            main_topic=main_topics[0],
            subtopic=main_topics[1],
            context=combined_texts,
            question_type=question_type,
            num_questions=num_questions
        )
        
        return {"questions": [q.dict() if hasattr(q, "dict") else str(q) for q in questions_response.questions]}, 200

# Register Namespaces
api.add_namespace(grammar_ns)
api.add_namespace(answer_ns)
api.add_namespace(generation_ns)

if __name__ == "__main__":
    app.run(debug=True)
