from index.document_query import *
from index.inverted_list import InvertedIndex
from preprocessing.preprocess import *

# Pipeline options for preprocessing
'''
"lowercase"
"remove-stopwords"
"remove-diacritics"
"remove-dates"
"remove-numbers"
"remove-html_tags"
"remove-punctuation"
"remove-urls"
"remove-time"
"lemmatization"
"stemming"
'''

# Pipeline
PIPELINE = ["lemmatization", "remove-diacritics", "lowercase"]


# Function for creating and adding a pipeline to index
def add_pipeline(pipeline_string: list[str]) -> PreprocessingPipeline:
    pipeline_temp = []

    for pipeline_name in pipeline_string:
        if pipeline_name == PreprocessType.LOWERCASE.value:
            pipeline_temp.append(LowercasePreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_STOPWORDS.value:
            pipeline_temp.append(RemoveStopwordsPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_DIACRITICS.value:
            pipeline_temp.append(RemoveDiacriticsPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_DATES.value:
            pipeline_temp.append(RemoveDatesPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_NUMBERS.value:
            pipeline_temp.append(RemoveNumbersPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_HTML_TAGS.value:
            pipeline_temp.append(RemoveHTMLtagsPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_PUNCTUATION.value:
            pipeline_temp.append(RemovePunctuationPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_URLS.value:
            pipeline_temp.append(RemoveURLsPreprocessor())

        elif pipeline_name == PreprocessType.REMOVE_TIME.value:
            pipeline_temp.append(RemoveTimePreprocessor())

        elif pipeline_name == PreprocessType.LEMMATIZATION.value:
            pipeline_temp.append(LematizationPreprocessor())

        elif pipeline_name == PreprocessType.STEMMING.value:
            pipeline_temp.append(StemmingPreprocessor())

        else:
            raise TypeError(f"Undefined pipeline:{pipeline_name}")

    return PreprocessingPipeline(pipeline_temp)


# Class representing Index
class OwnIndex:
    name: str
    content_to_index: list[str]
    documents: list[Document]
    documents_map: dict[str, Document]
    number_of_documents: int
    inverted_list: InvertedIndex
    vocabulary: list[DocumentTerm]
    visited_documents: set[str]
    preprocessing_pipeline: PreprocessingPipeline

    def __init__(self, name: str, content: list[str]):
        self.name = name
        self.content_to_index = content
        self.preprocessing_pipeline = add_pipeline(PIPELINE)
        self.visited_documents = set()

    # Function for adding Documents defined as strings
    def add_documents(self, list_of_documents: list[str]):
        i = 1

        self.documents = []
        self.documents_map = {}

        for data in list_of_documents:
            doc = Document(f"d{i}", data).tokenize()
            self.documents.append(doc)
            self.documents_map[doc.id] = doc
            i += 1

        self.number_of_documents = len(self.documents)

    # Function for adding Documents from .json or .jsonl a file
    def add_documents_json(self, json_data, evaluation: bool = False):
        i = 1

        self.documents = []
        self.documents_map = {}

        for data in json_data:

            text = ""
            for content in self.content_to_index:
                if data[content] is not None:
                    text += data[content]

            if evaluation:
                doc = Document(data["id"], text).tokenize()
            else:
                doc = Document(f"d{i}", text).tokenize()

            self.documents.append(doc)
            self.documents_map[doc.id] = doc
            i += 1

        self.number_of_documents = len(self.documents)

    # Function for getting Document by ID
    def get_document_by_id(self, id: str):
        return self.documents_map.get(id)

    # Function for sorting documents by similarity
    def sort_documents_by_similarity(self):
        # Sort documents based on similarity in descending order
        return sorted(self.documents, key=lambda doc: doc.similarity, reverse=True)
