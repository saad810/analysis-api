# Text Analysis API Documentation

## Overview
This API provides endpoints for grammar checking, answer validation, and question generation.

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Grammar Checking API
#### **Endpoint:** `/grammar/check`
- **Method:** `POST`
- **Description:** Checks grammar for the provided text.
- **Request Body:**
  ```json
  {
    "text": "Sample text to check."
  }
  ```
- **Response:**
  ```json
  {
    "results": [
      { "error": "Incorrect verb tense", "suggestion": "Use present tense" }
    ]
  }
  ```

### 2. Answer Validation API
#### **Endpoint:** `/answer/analyze`
- **Method:** `POST`
- **Description:** Validates the factual correctness of an answer.
- **Request Body:**
  ```json
  {
    "question": "What is the capital of France?",
    "user_answer": "Berlin",
    "subject": "Geography"
  }
  ```
- **Response:**
  ```json
  {
    "is_correct": false,
    "score": 0.2,
    "incorrect_facts": [
      { "statement": "Berlin is the capital of France", "explanation": "Paris is the correct answer." }
    ]
  }
  ```

### 3. Question Generation API
#### **Endpoint:** `/generate/questions`
- **Method:** `POST`
- **Description:** Generates questions based on provided subject and book.
- **Request Body:**
  ```json
  {
    "book": "History of Europe",
    "subject": "History",
    "num_questions": 5,
    "type": "multiple_choice"
  }
  ```
- **Response:**
  ```json
  {
    "questions": [
      "Who was the first emperor of Rome?",
      "What year did World War II start?"
    ]
  }
  ```

## Models

### GrammarCheckRequest
```json
{
  "text": "Text to check for grammar issues."
}
```

### AnswerValidationRequest
```json
{
  "question": "The question being asked.",
  "user_answer": "The user's response.",
  "subject": "Relevant subject area."
}
```

### GenerationRequest
```json
{
  "book": "Book or text title.",
  "subject": "Subject area.",
  "num_questions": 5,
  "type": "Type of questions to generate."
}
```

