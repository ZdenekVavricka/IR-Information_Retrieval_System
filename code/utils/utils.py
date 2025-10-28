import sys
import json
from typing import Iterable

from preprocessing.tokenizer import Token


# Class for printing to console and file
class PrintSave:
    def __init__(self, filename):
        self.file = open(filename, "w", encoding="utf-8")
        self.stdout = sys.stdout  # Keep a reference to the original stdout

    def write(self, text):
        self.stdout.write(text)  # Print to console
        self.file.write(text)  # Write to file

    def flush(self):
        self.stdout.flush()
        self.file.flush()

# Function loading data from .json or .jsonl files
def load_data(path: str):
    if path.endswith('.json'):
        with open(path, 'r') as f:
            return json.load(f)
    elif path.endswith('.jsonl'):
        data = []

        with open(path, 'r', encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
        return data
    else:
        raise ValueError('File extension must be .json or .jsonl')


# Function for replacing words
def replace_words(text: str, tokens: Iterable[Token]):
    operators = ["AND", "OR", "NOT", "(", ")"]

    replacements = []

    for token in tokens:
        if token.processed_form in operators:
            continue

        replacements.append({
            'start': token.position,
            'length': token.length,
            'original': token.original_form,
            'replacement': token.processed_form
        })

    replacements = sorted(replacements, key=lambda x: x['start'], reverse=True)

    for r in replacements:
        actual = text[r['start']:r['start'] + r['length']]
        if actual != r['original']:
            raise ValueError(f"Expected '{r['original']}' at {r['start']}, found '{actual}'")
        text = text[:r['start']] + r['replacement'] + text[r['start'] + r['length']:]

    return text