import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


# Enum token types
class TokenType(Enum):
    DATE = 1
    NUMBER = 2
    WORD = 3
    TAG = 4
    PUNCT = 5
    URL = 6
    TIME = 7


# Token class
@dataclass
class Token:
    original_form: str
    processed_form: str
    position: int
    length: int
    token_type: TokenType = TokenType.WORD

    def __repr__(self):
        return self.processed_form


# Tokenizer
class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, document: str) -> list[Token]:
        raise NotImplementedError()


# Split tokenizer
class SplitTokenizer(Tokenizer):
    def __init__(self, split_char: str):
        self.split_char = split_char

    def tokenize(self, document: str) -> list[Token]:
        tokens = []
        position = 0
        for word in document.split(self.split_char):
            token = Token(word, word, position, len(word))
            tokens.append(token)
            position += len(word) + 1
        return tokens


# Regex Match Tokenizer
class RegexMatchTokenizer(Tokenizer):
    num_pattern = r'(\d+[.,]?\d*)'  # matches numbers like 123, 123.123, 123,123
    word_pattern = r'(\w+)'  # matches words
    html_tag_pattern = r'(<.*?>)'  # matches html tags
    punctuation_pattern = r'([^\w\s]+)'  # matches punctuation
    date_pattern = r'(\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4})'  # matches dates like 12.12.2024
    url_pattern = r'((https?:\/\/|www\.)[^\s]+)'  # matches urls
    time_pattern = r'(\d+[:]?\d*)'  # matches time like 12:20
    default_pattern = f'{date_pattern}|{num_pattern}|{word_pattern}|{html_tag_pattern}|{punctuation_pattern}|{url_pattern}|{time_pattern}'

    # default_pattern = r'(\d+[.,](\d+)?)|([\w]+)|(<.*?>)|([^\w\s]+)'

    def __init__(self, pattern: str = default_pattern):
        self.pattern = pattern

    def tokenize(self, document: str) -> list[Token]:
        tokens = []
        for match in re.finditer(re.compile(self.pattern, re.UNICODE), document):
            token = Token(match.group(), match.group(), match.start(), match.end() - match.start(),
                          TokenType(match.lastindex))
            tokens.append(token)
        return tokens


if __name__ == '__main__':
    document = "Hello, world! This is a test."
    document1 = 'příliš žluťoučký kůň úpěl ďábelské ódy. 20.25'
    tokenizer = SplitTokenizer(" ")
    tokens = tokenizer.tokenize(document)
    print(tokens)
    tokenizer = RegexMatchTokenizer()
    tokens = tokenizer.tokenize(document)
    print(tokens)
