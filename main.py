

from index import store_pdf_in_pinecone
from index_queries import search_similar_materials,get_all_titles_in_subject,get_all_subjects
from config.pinecone import idx
from features.openai_config import client
import json
from features.grammar import grammar_check
from check_answer import validate_answer
from generate_questions import generate,extract_all_topics,generate_questions
def load_json_data(filepath: str):
    """Load JSON data from a file."""
    with open(filepath, "r", encoding='utf-8') as file:
        data = json.load(file)
    print("Imported JSON data")
    return data

def check_answer(question, answer,refrence,client,subject):
    results = search_similar_materials(query_text=question, client=client, subject=subject)
    


def main():
    # data = load_json_data("test/test-passages.json")
    # # # print(data['passage_1'])
    # sentence = data['passage_2']
    
    filename = "Beginning of World war 1.pdf"
    subject = "history"
    # store_pdf_in_pinecone(
    #     file_path="docs/Beginning of World war 1.pdf",
    #     client=client,
    #     subject=subject
    # )
    
 
 
    # sample_text = "This is an example sentence with error. And here is another one with, mistake"
    # query = "What caused World War 1?"
    # # subject = "history"
    # # results = search_similar_materials(query_text=query, client=client, subject=subject)
    # # print(results)
    # ans = validate_answer(question=query,subject=subject,client=client,user_answer=sentence)
    # print(ans)
    # subjects = get_all_subjects()
    # print(subjects[0])
    
    # results = get_all_titles_in_subject(subject=subjects[0])
    # print(results)
    
    results = generate(
        book="Beginning of World war 1",
        subject="history",
    )
    if not results:
        print("No text generated.")
        return
    # print(results)
    # print(results[0]['text'])
    # for result in results:
        # print(result['text'])
   
    topics = extract_all_topics(results)
    combined_texts = "\n".join(["\n".join(res["text"]) for res in results])
    # print(type(topics))
    print(topics)

    # Use the main_topics attribute from the TopicExtractionResponse object.
    main_topic_names = [sub.topic for sub in topics.main_topics]
    all_subtopics = [sub.subtopics for sub in topics.main_topics]

    # print(all_subtopics)
    # print(main_topic_names)
    
    # Generate questions using your function
    questions_response = generate_questions(
        main_topic=main_topic_names[0],
        subtopic=main_topic_names[1],
        context=combined_texts,
        num_questions=5
    )

# Extract the list of questions from the response object
    questions_list = questions_response.questions
    print(questions_list)
    # If the result is a tuple (with a label and a list), extract the list
    # if isinstance(questions, tuple):
    #     questions_list = questions[1]
    # else:
    #     questions_list = questions

    # # Sometimes, the questions_list itself may contain a nested tuple.
    # # For example, if it looks like: [('questions', [q1, q2, ...])]
    # if questions_list and isinstance(questions_list[0], tuple):
    #     # Extract the inner list of questions.
    #     question_texts = questions_list[0][1]
    # else:
    #     question_texts = questions_list

    # # Loop through and print each question on its own line
    # for idx, q in enumerate(question_texts, start=1):
    #     print(f"Question {idx}: {q}")

    # print(questions)/
#     if isinstance(questions, tuple):
#         questions_list = questions[1]
#     else:
#         questions_list = questions

# # Loop through and print each question individually:
#     for i, question in enumerate(questions_list, start=1):
#         print(f"Question {i}: {question}")

    
    # data = load_json_data("test/test-passages.json")
    # # print(data['passage_1'])
    # sentence = data['passage_1']
    # corrections = grammar_check(sentence)
    # for correction in corrections:
    #     print("Original:", correction.sentence)
    #     print("Corrected:", correction.corrected_sentence)
    #     print("Errors:", correction.errors)
    #     print("-" * 40)
    
    
    


if __name__ == "__main__":
    main()