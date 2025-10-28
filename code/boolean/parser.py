# AST Node Class definitions
class Node:
    # Function for evaluating node
    def evaluate(self, term_results, all_doc_ids):
        raise NotImplementedError()


# Class for term node
class TermNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Term({self.value})"

    def evaluate(self, term_results, all_doc_ids):
        return term_results.get(self.value, set())


# Class for NOT node
class NotNode(Node):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Not({self.child})"

    def evaluate(self, term_results, all_doc_ids):
        return all_doc_ids - self.child.evaluate(term_results, all_doc_ids)


# Class for AND node
class AndNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"And({self.left}, {self.right})"

    def evaluate(self, term_results, all_doc_ids):
        return self.left.evaluate(term_results, all_doc_ids) & self.right.evaluate(term_results, all_doc_ids)


# Class for OR node
class OrNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Or({self.left}, {self.right})"

    def evaluate(self, term_results, all_doc_ids):
        return self.left.evaluate(term_results, all_doc_ids) | self.right.evaluate(term_results, all_doc_ids)


# Class for SUB node
class SubNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Sub({self.left}, {self.right})"

    def evaluate(self, term_results, all_doc_ids):
        return self.left.evaluate(term_results, all_doc_ids) - self.right.evaluate(term_results, all_doc_ids)


# Function for comparing two nodes
def compare_nodes(node1, node2):
    if type(node1) != type(node2):
        return False

    if isinstance(node1, TermNode):
        return node1.value == node2.value

    elif isinstance(node1, NotNode):
        return compare_nodes(node1.child, node2.child)

    elif isinstance(node1, AndNode) or isinstance(node1, OrNode) or isinstance(node1, SubNode):
        return compare_nodes(node1.left, node2.left) and compare_nodes(node1.right, node2.right)

    return False


# Function for simplifying node expression
def simplify(node):
    while True:
        new_node = simplify_once(node)
        if compare_nodes(node, new_node):
            return node
        node = new_node


# Function for simplifying node expression once
def simplify_once(node):
    if isinstance(node, AndNode):
        left, right = simplify_once(node.left), simplify_once(node.right)

        # NOT Brutus AND Caesar → Caesar - Brutus
        if (isinstance(left, NotNode) and isinstance(left.child, Node)) and isinstance(right, Node):
            return SubNode(right, left.child)

        # NOT Caesar AND NOT Brutus → NOT (Caesar OR Brutus)
        if isinstance(left, NotNode) and isinstance(right, NotNode):
            return NotNode(OrNode(left.child, right.child))

        # Brutus AND NOT Caesar → Brutus - Caesar
        if isinstance(left, Node) and (isinstance(right, NotNode) and isinstance(right.child, Node)):
            return SubNode(left, right.child)

        return AndNode(left, right)

    elif isinstance(node, OrNode):
        left, right = simplify_once(node.left), simplify_once(node.right)

        # NOT Brutus OR Caesar → NOT (Brutus - Caesar)
        if (isinstance(left, NotNode) and isinstance(left.child, Node)) and isinstance(right, Node):
            return NotNode(SubNode(left.child, right))

        # NOT Brutus OR NOT Caesar → NOT (Brutus AND Caesar)
        if isinstance(left, NotNode) and isinstance(right, NotNode):
            return NotNode(AndNode(left.child, right.child))

        # Brutus OR NOT Caesar → NOT (Brutus - Caesar)
        if isinstance(left, Node) and (isinstance(right, NotNode) and isinstance(right.child, Node)):
            return NotNode(SubNode(right.child, left))

        return OrNode(left, right)

    elif isinstance(node, NotNode):
        return NotNode(simplify(node.child))

    elif isinstance(node, SubNode):
        return SubNode(simplify(node.left), simplify(node.right))

    return node


# Function for collecting terms from nodes
def collect_terms(node):
    terms = set()
    if isinstance(node, TermNode):
        terms.add(node.value)
    elif isinstance(node, NotNode):
        terms.update(collect_terms(node.child))
    elif isinstance(node, (AndNode, OrNode, SubNode)):
        terms.update(collect_terms(node.left))
        terms.update(collect_terms(node.right))
    return terms


# Recursive descent parser definition
# File: boolean/parser.py
import re

# Boolean Parser Class
class BooleanParser:
    """
    Lexical and syntax analyzer for boolean queries with the following grammar:
    expr: term (OR term)*
    term: factor (AND factor)*
    factor: [NOT] base
    base: LPAREN expr RPAREN | TERM
    """

    def __init__(self, text):
        self.tokens = self.tokenize(text)
        self.pos = 0

    @staticmethod
    def tokenize(text):
        token_spec = [
            ('AND', r'\bAND\b'),
            ('OR', r'\bOR\b'),
            ('NOT', r'\bNOT\b'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('TERM', r'[^\s\(\)]+'),
            ('SKIP', r'\S+'),
        ]
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        tokens = []
        for mo in re.finditer(tok_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            tokens.append((kind, value))
        return tokens

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None, None

    def consume(self, expected_kind=None):
        token = self.current_token()
        if token[0] is None:
            return token
        if expected_kind and token[0] != expected_kind:
            raise SyntaxError(f"Expected token {expected_kind} but got {token[0]}")
        self.pos += 1
        return token

    def parse(self):
        result = self.parse_expr()
        if self.current_token()[0] is not None:
            raise SyntaxError("Unexpected token at the end")
        return result

    def parse_expr(self):
        node = self.parse_term()
        while True:
            token = self.current_token()
            if token[0] == 'OR':
                self.consume('OR')
                right = self.parse_term()
                node = OrNode(node, right)
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_factor()
        while True:
            token = self.current_token()
            if token[0] == 'AND':
                self.consume('AND')
                right = self.parse_factor()
                node = AndNode(node, right)
            else:
                break
        return node

    def parse_factor(self):
        token = self.current_token()
        if token[0] == 'NOT':
            self.consume('NOT')
            # Parse only one NOT by parsing a base after consuming NOT.
            child = self.parse_base()
            return NotNode(child)
        else:
            return self.parse_base()

    def parse_base(self):
        token = self.current_token()
        if token[0] == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expr()
            self.consume('RPAREN')
            return node
        elif token[0] == 'TERM':
            term = self.consume('TERM')[1]
            return TermNode(term)
        else:
            raise SyntaxError("Unexpected token: " + str(token))


# Example usage:
if __name__ == "__main__":
    query = "apple AND (banana OR NOT cherry)"
    parser = BooleanParser(query)
    ast = parser.parse()
    print(ast)
