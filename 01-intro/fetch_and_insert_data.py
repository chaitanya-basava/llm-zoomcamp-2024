import requests
from elasticsearch import Elasticsearch


es_client = Elasticsearch('http://localhost:9200')
print(es_client.ping())

index_name = "datacamp-faqs"


if __name__ == "__main__":
    docs_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1'
    docs_response = requests.get(docs_url)
    documents_raw = docs_response.json()

    documents = []

    for course in documents_raw:
        course_name = course['course']

        for doc in course['documents']:
            doc['course'] = course_name
            es_client.index(index=index_name, document=doc)
