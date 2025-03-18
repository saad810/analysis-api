from langdetect import detect
import re
from typing import List
from pydantic import BaseModel
from features.openai_config import client

def split_english(text: str):
    detected_lang = detect(text)
    if detected_lang != "en":
        raise ValueError(f"Text is not in English. Detected language: {detected_lang}")
    return re.split(r'(?<=[.!?,:;…])\s+|(?<=\.\.\.)\s+', text.strip())

class GrammarModel(BaseModel):
    sentence: str
    corrected_sentence: str
    errors: List[str]  # Explicitly specify list items as strings

def grammar(sentence: str) -> GrammarModel:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system", 
                "content": (
                    "Correct only the grammatical errors in the provided sentence. "
                    "Do not change or remove any factual information, even if it appears incorrect. "
                    "Focus solely on grammar, punctuation, and capitalization. "
                    "Return your response as JSON with keys: 'sentence', 'corrected_sentence', and 'errors'."
                )
            },
            {"role": "user", "content": sentence},
        ],
        response_format=GrammarModel,
    )
    return completion.choices[0].message.parsed

def grammar_check(text: str):
    sentences = split_english(text)
    results = []
    for sentence in sentences:
        result = grammar(sentence)
        results.append(result)
    return results

if __name__ == "__main__":
    sample_text = "This is an example sentence with error. And here is another one with, mistake"
    corrections = grammar_check(sample_text)
    
    for correction in corrections:
        print("Original:", correction.sentence)
        print("Corrected:", correction.corrected_sentence)
        print("Errors:", correction.errors)
        print("-" * 40)
