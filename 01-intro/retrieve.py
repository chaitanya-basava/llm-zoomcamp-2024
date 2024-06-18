import json
import tiktoken
from elasticsearch import Elasticsearch


es_client = Elasticsearch('http://localhost:9200')
print(es_client.ping())

index_name = "datacamp-faqs"


def elastic_search(query):
    search_query = {
        "size": 3,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^4", "text"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "machine-learning-zoomcamp"
                    }
                }
            }
        }
    }

    return es_client.search(index=index_name, body=search_query)


def build_prompt(retrievals, question):
    context_template = """
Q: {question}
A: {text}
    """.strip()

    context = ""
    for i, retrieval in enumerate(retrievals):
        retrieval = retrieval["_source"]
        context += context_template.format(question=retrieval["question"], text=retrieval["text"])
        if i < len(retrievals) - 1:
            context += "\n\n"

    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
    """.strip()

    return prompt_template.format(question=question, context=context)


if __name__ == "__main__":
    query = "How do I execute a command in a running docker container?"

    response = elastic_search(query)
    print(json.dumps(response.raw, indent=4))

    prompt = build_prompt(response.raw.get("hits").get("hits"), query)

    print(prompt)
    print(f"\n\nPrompt length: {len(prompt)}")

    encoding = tiktoken.encoding_for_model("gpt-4o")
    print(f"#token: {len(encoding.encode(prompt))}")
