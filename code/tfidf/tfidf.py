import numpy as np

from index.index import OwnIndex
from index.inverted_list import *


# Function for calculating tf-weight
def calc_tf_weight(vocabulary: list):
    for term in vocabulary:
        if term.tf == 0:
            term.tf_weight = 0
        else:
            term.tf_weight = 1 + np.log10(term.tf)


# Function for calculating n'lized
def calc_n_lized(vocabulary: list):
    temp = 0
    for term in vocabulary:
        temp += term.tf_weight * term.tf_weight

    norm = np.sqrt(temp)

    for term in vocabulary:
        if norm != 0:
            term.n_lized = term.tf_weight / norm
        else:
            term.n_lized = 0


# Function for calculating df
def calc_df(index: OwnIndex, vocabulary: list):
    for term in vocabulary:
        if index.inverted_list.exists(term.term):
            term.df = index.inverted_list.term_document_count(term.term)


# Function for calculating idf
def calc_idf(index: OwnIndex, vocabulary: list):
    for term in vocabulary:
        if term.df != 0:
            term.idf = np.log10(index.number_of_documents / term.df)


# Function for calculating q-weight
def calc_q_weight(vocabulary: list):
    for term in vocabulary:
        if term.idf != 0:
            term.q_weight = term.tf * term.idf


# Function for calculating cosine similarity for each document
def calc_similarity(index: OwnIndex, query: Query):
    reset_similarity(index)

    # Calculation of similarity
    for query_term in query.vocabulary:
        for doc_id in index.inverted_list.search(query_term.term):
            document = index.get_document_by_id(doc_id)

            if doc_id not in index.visited_documents:
                index.visited_documents.add(doc_id)

            doc_term = document.vocabulary_map.get(query_term.term)

            if doc_term.term:
                document.similarity += doc_term.n_lized * query_term.q_weight

def reset_similarity(index: OwnIndex):
    for doc_id in index.visited_documents:
        document = index.get_document_by_id(doc_id)
        document.similarity = 0

    index.visited_documents.clear()


# Function for printing TfIdf attributes of document/query
def display_tfidf(components: Iterable[IRComponent]):
    for component in components:
        if isinstance(component, Query):
            for term in component.vocabulary:
                print("Term: " + term.term + ", tf: " + str(term.tf) + ", tf-weight: " + str(
                    term.tf_weight) + ", df: " + str(term.df) + ", idf: " + str(term.idf) + ", q_weight: " + str(
                    term.q_weight))
        elif isinstance(component, Document):
            for term in component.vocabulary:
                print("Term: " + term.term + ", tf: " + str(term.tf) + ", tf-weight: " + str(
                    term.tf_weight) + ", n'lized: " + str(term.n_lized))
        else:
            raise TypeError(f"Unsupported component type: {type(component)}")
