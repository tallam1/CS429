import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from flask import Flask

app = Flask(__name__)

# Load the TF-IDF matrix and feature names if they are stored in the pickle file.
try:
    with open('/Users/tonyallam/Desktop/Cs429/cs429project/cs429project/flask/inverted_index.pkl', 'rb') as inp:
        inverted_index = pickle.load(inp)
        if isinstance(inverted_index, (np.ndarray, np.matrix)):
            print("Loaded TF-IDF matrix successfully.")
        else:
            print("Loaded data is not a matrix. Please check the pickle file.")
except FileNotFoundError:
    print("File not found. Please verify the path to the pickle file.")
except Exception as e:
    print(f"An error occurred: {e}")

# Assuming `vectorizer` needs to be fitted or loaded as well:
# Load or fit your TfidfVectorizer here

# Function to handle queries:
def process_query(query):
    if not query:
        raise ValueError("Query is required")

    try:
        # Ensure the vectorizer is fitted before transforming documents
        # Placeholder for fitting the vectorizer if necessary
        # vectorizer.fit([some_training_data])

        # Transform the query into tf-idf features
        results = vectorizer.transform([query])
        cosine_similarities = np.dot(results, inverted_index.T).toarray().flatten()
        print(cosine_similarities)
    except Exception as e:
        print(f"Error processing query: {e}")

if __name__ == '__main__':
    query = "example query text"
    process_query(query)
