from collections import Counter
from typing import Iterable

from index.term import DocumentTerm, QueryTerm, Term
from preprocessing.preprocess import PreprocessingPipeline
from preprocessing.tokenizer import Tokenizer, RegexMatchTokenizer


# Base class for Document and Query
class IRComponent:
    id: str
    text: str

    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text
        self.tokens = None
        self.vocabulary = None

    # Function for tokenizing text
    def tokenize(self, tokenizer: Tokenizer = None):
        tokenizer = tokenizer or RegexMatchTokenizer()
        self.tokens = tokenizer.tokenize(self.text)
        return self

    # Function for preprocessing tokens
    def preprocess(self, preprocessing_pipeline: PreprocessingPipeline):
        self.tokens = [token for token in preprocessing_pipeline.preprocess(self.tokens, self.text) if
                       token is not None]
        return self

# Class for Document
class Document(IRComponent):
    vocabulary: list[DocumentTerm]
    vocabulary_map = {}
    similarity: float

    def __init__(self, id: str, text: str):
        super().__init__(id, text)
        self.similarity = 0
        self.vocabulary_map = {}

# Class for Query
class Query(IRComponent):
    vocabulary: list[QueryTerm]
    list_of_id_documents: set[str]

    def __init__(self, id: str, text: str):
        super().__init__(id, text)
        self.list_of_id_documents = set()

# Function for building vocabulary from all documents
def build_complete_vocabulary(components: Iterable[IRComponent]):
    counter = Counter()

    for component in components:
        counter.update((token.processed_form for token in component.tokens))

    vocabulary = []

    for key, value in counter.items():
        vocabulary.append(Term(key, value))

    return vocabulary


# Function for building vocabulary of one document
def build_vocabulary(component: IRComponent):
    counter = Counter()
    counter.update((token.processed_form for token in component.tokens))

    vocabulary = []

    for key, value in counter.items():
        if isinstance(component, Document):
            term = DocumentTerm(key, value)
            vocabulary.append(term)
            component.vocabulary_map[key] = term
        else:
            vocabulary.append(QueryTerm(key, value))

    return vocabulary
