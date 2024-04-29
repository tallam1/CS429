def query_process(query):
    if not query:
        return "Query is empty."
    
    # Remove non-letter symbols and convert to lower case
    new_query = re.sub(r'[^a-zA-Z\s]', '', query).lower()
    new_query_li = new_query.split()
    query_cleaned = ' '.join([word for word in new_query_li if word not in stop_words])

    # Transform the cleaned query into a TF-IDF vector
    query_vector = transformer_vector.transform([query_cleaned])
    if query_vector.shape[1] == 0:
        return "Query vector is empty after transformation. No known terms."

    # Initialize document vectors
    num_documents = len(url_to_index)
    num_terms = len(invert_ind)
    document_vectors = np.zeros((num_terms, num_documents))

    for term_idx, term in enumerate(invert_ind.keys()):
        for url, tfidf_matrix in invert_ind[term]:
            tfidf_score = tfidf_matrix.data[0] if tfidf_matrix.nnz > 0 else 0
            doc_idx = url_to_index[url]
            document_vectors[term_idx, doc_idx] = tfidf_score

    # Calculate norms using appropriate functions
    norm_query = sparse_norm(query_vector) + 1e-10
    norm_documents = np.linalg.norm(document_vectors, axis=0) + 1e-10


    # Example to print feature names and check if a term is in the vocabulary
    feature_names = transformer_vector.get_feature_names_out()
    print("Feature names include:", 'papers' in feature_names, 'robots' in feature_names)

    print("Norm of query vector:", norm_query)
    print("Norms of document vectors:", norm_documents)