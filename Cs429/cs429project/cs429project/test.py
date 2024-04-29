import re
import  numpy as np
from scipy.sparse.linalg import norm as sparse_norm
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
import pickle
import json
from collections import defaultdict


stop_words = set(stopwords.words('english'))

# Initialize a defaultdict with the factory function
invert_ind = defaultdict(list)
# Add tuples to the list for each key
with open(r'C:\\Users\\Rudra More\\Desktop\\CS429_project\\htmlscraper\\htmlscraper\\inverted_index.pkl', 'rb') as inp:
    invert_ind = pickle.load(inp)

unique_urls = set()
for postings in invert_ind.values():
    for url, _ in postings:
        unique_urls.add(url)

# convert the set to a list to index the URLs consistently.
unique_urls = list(unique_urls)

# Create a mapping from URLs to indices
url_to_index = {url: idx for idx, url in enumerate(unique_urls)}
with open(r'C:\Users\Rudra More\Desktop\CS429_project\htmlscraper\htmlscraper\vector_tranform_matrix', 'rb') as tv:
    transformer_vector = pickle.load(tv)

with open(r'C:\Users\Rudra More\Desktop\CS429_project\htmlscraper\htmlscraper\urls_title.pkl', 'rb') as url_t:
    url_to_title = pickle.load(url_t)




def query_process():

    with open('search_query.json', 'r') as reader:
        query_text = json.load(reader)

    query = query_text.get('search_query', '')

    print("Processing query...")
    
        # Handles "top x documents in topic", "top documents in topic", or just "topic"
    match = re.match(r"(top\s*(\d*)\s*documents in\s+)?(.+)", query.lower().strip())
    if match:
        top_x = int(match.group(2)) if match.group(2) else 10  # Default to 10 if not specified
        topic = match.group(3)


        new_query = re.sub(r'[^a-zA-Z\s]', '', topic).lower()
        new_query_li = new_query.split()
        query_cleaned = ' '.join([word for word in new_query_li if word not in stop_words])

        query_vector = transformer_vector.transform([query_cleaned])
        print("Query vector shape:", query_vector.shape)

        if query_vector.shape[1] == 0:
            print("Query vector is empty after transformation.")
            return "Query vector is empty after transformation."

        num_documents = len(unique_urls)
        num_terms = len(invert_ind)
        document_vectors = np.zeros((num_terms, num_documents))

        # Mapping scores and titles to the URLs
        results_with_titles = []

        for term_idx, term in enumerate(invert_ind.keys()):
            for url, tfidf_score in invert_ind[term]:
                doc_idx = url_to_index.get(url, -1)
                if doc_idx != -1:
                    document_vectors[term_idx, doc_idx] = tfidf_score

        # Initialize results_with_titles once for each unique document
        results_with_titles = [(idx, url_to_title.get(url, "No title available"), url) for idx, url in enumerate(unique_urls)]

        norm_query = sparse_norm(query_vector) + 1e-10
        norm_documents = np.linalg.norm(document_vectors, axis=0) + 1e-10
        cosine_similarities = (query_vector.dot(document_vectors) / (norm_query * norm_documents)).flatten().tolist()

        # Combine URLs, titles, and scores
        scored_results = [(title, url, cosine_similarities[doc_idx]) for doc_idx, title, url in results_with_titles]

        # Sort by score in descending order
        sorted_results = sorted(scored_results, key=lambda x: x[2], reverse=True)

        # Only return the sorted URLs and titles with their scores
        return sorted_results[:top_x]