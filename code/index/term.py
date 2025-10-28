# Term class
class Term:
    term: str
    tf: int

    def __init__(self, term: str, tf: int):
        self.term = term
        self.tf = tf


# Term class for document
class DocumentTerm(Term):
    tf_weight: float
    n_lized: float

    def __init__(self, term: str, tf: int):
        super().__init__(term, tf)
        self.tf_weight = 0
        self.n_lized = 0


# Term class for query
class QueryTerm(Term):
    tf_weight: float
    df: int
    idf: float
    q_weight: float

    def __init__(self, term: str, tf: int):
        super().__init__(term, tf)
        self.tf_weight = 0
        self.df = 0
        self.idf = 0
        self.q_weight = 0