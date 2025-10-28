from typing import Iterable

from index.document_query import Query
from index.eval_interface import process_tfidf, preprocess_query, process_boolean, preprocess_document
from index.index import OwnIndex


class Index:
    own_index: OwnIndex

    def __init__(self):
        pass

    def index_documents(self, documents: Iterable[dict[str, str]]):
        self.own_index = OwnIndex("eval", ["title", "text"])
        self.own_index.add_documents_json(documents, True)
        preprocess_document(self.own_index)

    def get_document(self, doc_id: str) -> dict[str, str]:
        doc = self.own_index.get_document_by_id(doc_id)
        return {doc_id: doc.text}


class SearchEngine:
    def __init__(self, index: Index):
        self.index = index

    def search(self, query: str) -> list[tuple[str, float]]:
        query = Query("q1", query)

        preprocess_query(query, self.index.own_index, True)

        result = process_tfidf(self.index.own_index, query)

        return sorted(result, key=lambda x: x[1], reverse=True)

    def boolean_search(self, query: str) -> set[str]:
        query = Query("q1", query)

        preprocess_query(query, self.index.own_index)

        return process_boolean(self.index.own_index, query)
