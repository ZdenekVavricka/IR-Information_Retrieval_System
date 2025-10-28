from boolean.parser import BooleanParser, simplify, collect_terms
from tfidf.tfidf import *
from utils.utils import replace_words


# Function for processing tfidf
def process_tfidf(index: OwnIndex, query: Query):
    calc_similarity(index, query)

    result = []

    for doc in index.documents:
        if doc.similarity != 0:
            result.append((doc.id, doc.similarity))

    return result


# Function for processing boolean
def process_boolean(index: OwnIndex, query: Query):
    all_doc_ids = index.inverted_list.get_all_document_ids()

    query.text = replace_words(query.text, query.tokens)

    parser = BooleanParser(query.text)
    ast = parser.parse()
    terms = collect_terms(ast)
    term_results = {term: index.inverted_list.search(term) for term in terms}

    simplify_ast = simplify(ast)

    return simplify_ast.evaluate(term_results, all_doc_ids)


# Function for preprocessing
def preprocess(components: Iterable[IRComponent], preprocessing_pipeline: PreprocessingPipeline):
    [component.tokenize() for component in components]

    components_ = [component.preprocess(preprocessing_pipeline) for component in components]

    for component in components_:
        component.vocabulary = build_vocabulary(component)


# Function for preprocessing documents
def preprocess_document(index: OwnIndex):
    preprocess(index.documents, index.preprocessing_pipeline)

    index.vocabulary = build_complete_vocabulary(index.documents)

    index.inverted_list = index_all_documents(index.documents)

    for doc in index.documents:
        calc_tf_weight(doc.vocabulary)
        calc_n_lized(doc.vocabulary)


# Function for preprocessing queries
def preprocess_query(query: Query, index: OwnIndex, tfidf: bool = False):
    preprocess([query], index.preprocessing_pipeline)

    if tfidf:
        calc_tf_weight(query.vocabulary)
        calc_df(index, query.vocabulary)
        calc_idf(index, query.vocabulary)
        calc_q_weight(query.vocabulary)

        for term in query.vocabulary:
            for id in index.inverted_list.search(term.term):
                query.list_of_id_documents.add(id)


# Function for printing results with limit
def print_sorted_documents(index: OwnIndex, query: Query, limit: int = 0):
    i = 1

    sorted_documents = index.sort_documents_by_similarity()

    print(f"Query ID: {query.id}, Text: {query.text}\n")

    for doc in sorted_documents:
        if doc.similarity == 0:
            break

        if limit != 0:
            if i <= limit:
                print(f"Document ID: {doc.id}, Similarity: {doc.similarity:.4f}, Text: {doc.text}")
            i += 1
        else:
            print(f"Document ID: {doc.id}, Similarity: {doc.similarity:.4f}, Text: {doc.text}")

    print()
    print("-" * 100)
    print()
