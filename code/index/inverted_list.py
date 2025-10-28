from collections import defaultdict

from index.document_query import *



# Class for inverted list
class InvertedIndex:

    def __init__(self):
        self.index = defaultdict(set)  # Stores term -> set of document IDs

    # Function for adding a document
    def add_document(self, doc_id, vocabulary):
        # Adds a document to the inverted index using pre-tokenized words.
        for term in vocabulary:
            self.index[term.term].add(doc_id)

    # Function for searching term and returns the list of document IDs containing the term.
    def search(self, query):
        return self.index.get(query, set())

    # Function for checking if a term exists in the index.
    def exists(self, token):
        return token in self.index

    # Function for printing a whole inverted list
    def display(self):
        # Displays the inverted index.
        for term, doc_ids in self.index.items():
            print(f"{term}: {sorted(doc_ids)}")

    # Function for computing number of documents containing the given term
    def term_document_count(self, term):
        return len(self.index.get(term, set()))

    # Function for getting all document id's
    def get_all_document_ids(self):
        all_doc_ids = set()
        for doc_ids in self.index.values():
            all_doc_ids.update(doc_ids)
        return all_doc_ids


# Function for indexing all documents
def index_all_documents(documents: Iterable[Document]):
    index = InvertedIndex()

    for doc in documents:
        index.add_document(doc.id, doc.vocabulary)

    return index
