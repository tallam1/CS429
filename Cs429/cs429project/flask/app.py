import pickle
import re
import json
import numpy as np
from flask import Flask, request, jsonify
import nltk
nltk.download('stopwords', quiet = True)
from nltk.corpus import stopwords # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from scipy.sparse.linalg import norm as sparse_norm

app = Flask(__name__)

vectorizer = TfidfVectorizer()

invert_index1 = defaultdict(tuple)
stop_words = set(stopwords.words('english'))

with open(r'/Users/tonyallam/Desktop/Cs429/cs429project/cs429project/inverted_index.pkl', 'rb') as inp:
     inverted_index = pickle.load(inp)

u_urls = set()
for postings in inverted_index.values():
    for url, _ in postings:
        u_urls.add(url)

u_urls = list(u_urls)

url_to_index = {url: idx for idx, url in enumerate(u_urls)}
with open(r'/Users/tonyallam/Desktop/Cs429/cs429project/cs429project/vectorizer.pkl', 'rb') as tv:
    trans_vector = pickle.load(tv)

with open(r'/Users/tonyallam/Desktop/Cs429/cs429project/cs429project/url_title_mapping.pkl','rb') as url_t:
    url_title = pickle.load(url_t)

# Endpoint to handle text queries
def process_query():

    with open('search_data.json', 'r') as reader:
        query_text = json.load(reader)

    query = query_text.get('search_query', '')

    print("Processing query...")
    print("test")
    match = re.match(r"(top\s*(\d*)\s*documents in\s+)?(.+)", query.lower().strip())
    if match:
        top_x = int(match.group(2)) if match.group(2) else 10  # Default to 10 if not specified
        topic = match.group(3)

        new_query = re.sub(r'[^a-zA-Z\s]', '', topic).lower()
        new_query_li = new_query.split()
        query_cleaned = ' '.join([word for word in new_query_li if word not in stop_words])

        query_vector = trans_vector.transform([query_cleaned])
        print("Query vector shape:", query_vector.shape)
        if query_vector.shape[1] == 0:
            print("Query vector is empty after transformation.")
            return "Query vector is empty after transformation."
        
        num_documents = len(u_urls)
        num_terms = len(inverted_index)
        document_vectors = np.zeros((num_terms, num_documents))

        # Mapping scores and titles to the URLs
        results_with_titles = []

        for term_idx, term in enumerate(inverted_index.keys()):
            for url, tfidf_score in inverted_index[term]:
                doc_idx = url_to_index.get(url, -1)
                if doc_idx != -1:
                    # tfidf_score_array = tfidf_score.toarray()[0]
                    document_vectors[term_idx, doc_idx] = tfidf_score
        # Initialize results_with_titles once for each unique document
        results_w_titles = [(idx, url_title.get(url, "No title available"), url) for idx, url in enumerate(u_urls)]

        norm_query = sparse_norm(query_vector) 
        norm_documents = np.linalg.norm(document_vectors, axis=0)
        print("This is a document vector shape" , document_vectors.shape)
        print("this is a query vector shape" , query_vector.shape)
        cosine_similarities = ((query_vector.dot(document_vectors)) / (norm_query * norm_documents)).flatten().tolist()

        # Combine URLs, titles, and scores
        scored_results = [(title, url, cosine_similarities[doc_idx]) for doc_idx, title, url in results_w_titles]

        # Sort by score in descending order
        sorted_results = sorted(scored_results, key=lambda x: x[2], reverse=True)

        # Only return the sorted URLs and titles with their scores
        return sorted_results[:top_x]



# if __name__ == '__main__':
#     #app.run(debug=True)
#     query = 'oppenheimer'
#     print(process_query(query))
#     print("test")