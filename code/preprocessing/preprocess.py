from abc import ABC, abstractmethod
from typing import Optional

from enum import Enum

from unidecode import unidecode

from preprocessing import czech_stemmer
from preprocessing.tokenizer import Token, TokenType

import majka


class PreprocessType(Enum):
    LOWERCASE = "lowercase"
    REMOVE_STOPWORDS = "remove-stopwords"
    REMOVE_DIACRITICS = "remove-diacritics"
    REMOVE_DATES = "remove-dates"
    REMOVE_NUMBERS = "remove-numbers"
    REMOVE_HTML_TAGS = "remove-html_tags"
    REMOVE_PUNCTUATION = "remove-punctuation"
    REMOVE_URLS = "remove-urls"
    REMOVE_TIME = "remove-time"
    LEMMATIZATION = "lemmatization"
    STEMMING = "stemming"

# Token Preprocessor Class
class TokenPreprocessor(ABC):
    type: PreprocessType

    OPERATORS = ["AND", "OR", "NOT"]

    # Preprocessing function for token
    @abstractmethod
    def preprocess(self, token: Token, document: str) -> Token:
        raise NotImplementedError()

    # Preprocessing function for all tokens and pipelines
    def preprocess_all(self, tokens: list[Token], document: str) -> list[Token]:
        contains_operator = any(token.processed_form in self.OPERATORS for token in tokens)
        allowed_preprocess_types_if_boolean = [PreprocessType.LOWERCASE.value, PreprocessType.REMOVE_DIACRITICS,
                                               PreprocessType.LEMMATIZATION.value,
                                               PreprocessType.STEMMING.value]

        if contains_operator and (self.type.value not in allowed_preprocess_types_if_boolean):
            return tokens

        result = []
        for token in tokens:
            if token.processed_form in self.OPERATORS:
                result.append(token)
                continue

            token_processed = self.preprocess(token, document)

            if token_processed is not None:
                result.append(token_processed)

        return result

# Preprocessing function for changing UpperCase to LowerCase
class LowercasePreprocessor(TokenPreprocessor):
    type = PreprocessType.LOWERCASE

    def preprocess(self, token: Token, document: str) -> Token:
        token.processed_form = token.processed_form.lower()
        return token


# Preprocessing function for removing stopwords
class RemoveStopwordsPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_STOPWORDS

    STOP_WORDS = [
        # Stop words without diacritics
        "a", "s", "k", "o", "i", "u", "v", "z", "dnes", "cz", "timto", "budes", "budem", "byli", "jses",
        "muj", "svym", "ta", "tomto", "tohle", "tuto", "tyto", "jej", "zda", "proc", "mate", "tato", "kam",
        "tohoto", "kdo", "kteri", "mi", "nam", "tom", "tomuto", "mit", "nic", "proto", "kterou", "byla",
        "toho", "protoze", "asi", "ho", "nasi", "napiste", "re", "coz", "tim", "takze", "svych", "jeji",
        "svymi", "jste", "aj", "tu", "tedy", "teto", "bylo", "kde", "ke", "prave", "ji", "nad", "nejsou",
        "ci", "pod", "tema", "mezi", "pres", "ty", "pak", "vam", "ani", "kdyz", "vsak", "neg", "jsem",
        "tento", "clanku", "clanky", "aby", "jsme", "pred", "pta", "jejich", "byl", "jeste", "az", "bez",
        "take", "pouze", "prvni", "vase", "ktera", "nas", "novy", "tipy", "pokud", "muze", "strana", "jeho",
        "sve", "jine", "zpravy", "nove", "neni", "vas", "jen", "podle", "zde", "uz", "byt", "vice", "bude",
        "jiz", "nez", "ktery", "by", "ktere", "co", "nebo", "ten", "tak", "ma", "pri", "od", "po", "jsou",
        "jak", "dalsi", "ale", "si", "se", "ve", "to", "jako", "za", "zpet", "ze", "do", "pro", "je", "na",
        "atd", "atp", "jakmile", "pricemz", "ja", "on", "ona", "ono", "oni", "ony", "my", "vy", "ji", "me",
        "mne", "jemu", "tomu", "tem", "temu", "nemu", "nemuz", "jehoz", "jiz", "jelikoz", "jez", "jakoz",
        "nacez", "ackoli", "ahoj", "anebo", "ano", "aspon", "behem", "beze", "blizko", "bohuzel", "brzo",
        "budeme", "budete", "budou", "budu", "byly", "bys", "cau", "chce", "chceme", "chces", "chcete",
        "chci", "chteji", "chtit", "chut", "chuti", "ctrnact", "ctyri", "dal", "dale", "daleko", "dekovat",
        "dekujeme", "dekuji", "den", "deset", "devatenact", "devet", "dobry", "docela", "dva", "dvacet",
        "dvanact", "dve", "hodne", "jde", "jeden", "jedenact", "jedna", "jedno", "jednou", "jedou", "jenom",
        "jestli", "jestlize", "jich", "jim", "jimi", "jinak", "jsi", "kdy", "kolik", "krome", "kvuli", "maji",
        "malo", "mam", "mame", "mas", "me", "mi", "mne", "mnou", "moc", "mohl", "mohou", "moje", "moji",
        "mozna", "musi", "nade", "nami", "naproti", "nas", "nase", "ne", "ne", "nebyl", "nebyla", "nebyli",
        "nebyly", "neco", "nedela", "nedelaji", "nedelam", "nedelame", "nedelas", "nedelate", "nejak",
        "nejsi", "nekde", "nekdo", "nemaji", "nemame", "nemate", "nemel", "nestaci", "nevadi", "nich",
        "nim", "nimi", "nula", "ode", "osm", "osmnact", "patnact", "pet", "porad", "potom", "pozde", "prese",
        "prosim", "proste", "proti", "rovne", "sedm", "sedmnact", "sest", "sestnact", "skoro", "smeji",
        "smi", "snad", "spolu", "sta", "ste", "sto", "tady", "takhle", "taky", "tam", "tamhle", "tamhleto",
        "tamto", "te", "tebe", "tebou", "ted", "ti", "tisic", "tisice", "tobe", "toto", "treba", "tri",
        "trinact", "trosku", "tva", "tve", "tvoje", "tvuj", "urcite", "vami", "vas", "vasi", "vecer",
        "vedle", "vlastne", "vsechno", "vsichni", "vubec", "vzdy", "zac", "zatimco", "ze",

        # Stop words with diacritics
        "a", "s", "k", "o", "i", "u", "v", "z", "dnes", "cz", "tímto", "budeš", "budem", "byli", "jseš",
        "můj", "svým", "ta", "tomto", "tohle", "tuto", "tyto", "jej", "zda", "proč", "máte", "tato", "kam",
        "tohoto", "kdo", "kteří", "mi", "nám", "tom", "tomuto", "mít", "nic", "proto", "kterou", "byla",
        "toho", "protože", "asi", "ho", "naši", "napište", "re", "což", "tím", "takže", "svých", "její",
        "svými", "jste", "aj", "tu", "tedy", "teto", "bylo", "kde", "ke", "pravé", "ji", "nad", "nejsou",
        "či", "pod", "téma", "mezi", "přes", "ty", "pak", "vám", "ani", "když", "však", "neg", "jsem",
        "tento", "článku", "články", "aby", "jsme", "před", "pta", "jejich", "byl", "ještě", "až", "bez",
        "také", "pouze", "první", "vaše", "která", "nás", "nový", "tipy", "pokud", "může", "strana", "jeho",
        "své", "jiné", "zprávy", "nové", "není", "vás", "jen", "podle", "zde", "už", "být", "více", "bude",
        "již", "než", "který", "by", "které", "co", "nebo", "ten", "tak", "má", "při", "od", "po", "jsou",
        "jak", "další", "ale", "si", "se", "ve", "to", "jako", "za", "zpět", "ze", "do", "pro", "je", "na",
        "atd", "atp", "jakmile", "přičemž", "já", "on", "ona", "ono", "oni", "ony", "my", "vy", "jí", "mě",
        "mne", "jemu", "tomu", "těm", "těmu", "němu", "němuž", "jehož", "jíž", "jelikož", "jež", "jakož",
        "načež", "ačkoli", "ahoj", "anebo", "ano", "aspoň", "během", "beze", "blízko", "bohužel", "brzo",
        "budeme", "budete", "budou", "budu", "byly", "bys", "čau", "chce", "chceme", "chceš", "chcete",
        "chci", "chtějí", "chtít", "chut'", "chuti", "čtrnáct", "čtyři", "dál", "dále", "daleko", "děkovat",
        "děkujeme", "děkuji", "den", "deset", "devatenáct", "devět", "dobrý", "docela", "dva", "dvacet",
        "dvanáct", "dvě", "hodně", "jde", "jeden", "jedenáct", "jedna", "jedno", "jednou", "jedou", "jenom",
        "jestli", "jestliže", "jich", "jím", "jimi", "jinak", "jsi", "kdy", "kolik", "kromě", "kvůli", "mají",
        "málo", "mám", "máme", "máš", "mé", "mí", "mně", "mnou", "moc", "mohl", "mohou", "moje", "moji",
        "možná", "musí", "nade", "námi", "naproti", "náš", "naše", "ne", "ně", "nebyl", "nebyla", "nebyli",
        "nebyly", "něco", "nedělá", "nedělají", "nedělám", "neděláme", "neděláš", "neděláte", "nějak",
        "nejsi", "někde", "někdo", "nemají", "nemáme", "nemáte", "neměl", "nestačí", "nevadí", "nich",
        "ním", "nimi", "nula", "ode", "osm", "osmnáct", "patnáct", "pět", "pořád", "potom", "pozdě", "přese",
        "prosím", "prostě", "proti", "rovně", "sedm", "sedmnáct", "šest", "šestnáct", "skoro", "smějí",
        "smí", "snad", "spolu", "sta", "sté", "sto", "tady", "takhle", "taky", "tam", "tamhle", "tamhleto",
        "tamto", "tě", "tebe", "tebou", "ted'", "ti", "tisíc", "tisíce", "tobě", "toto", "třeba", "tři",
        "třináct", "trošku", "tvá", "tvé", "tvoje", "tvůj", "určitě", "vámi", "váš", "vaši", "večer",
        "vedle", "vlastně", "všechno", "všichni", "vůbec", "vždy", "zač", "zatímco", "že"
    ]

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        if token.processed_form in self.STOP_WORDS:
            return None
        return token

# Preprocessing function for removing diacritics
class RemoveDiacriticsPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_DIACRITICS

    def preprocess(self, token: Token, document: str) -> Token:
        token.processed_form = unidecode(token.processed_form)
        return token


# Preprocessing function for removing dates
class RemoveDatesPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_DATES

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        if token.token_type == TokenType.DATE:
            return None
        return token

# Preprocessing function for removing number
class RemoveNumbersPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_NUMBERS

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        if token.token_type == TokenType.NUMBER:
            return None
        return token

# Preprocessing function for removing HTML tags
class RemoveHTMLtagsPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_HTML_TAGS

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        if token.token_type == TokenType.TAG:
            return None
        return token

# Preprocessing function for removing punctuation
class RemovePunctuationPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_PUNCTUATION

    def preprocess(self, token: Token, document: str, prev_token: Token = None,
                   next_token: Token = None) -> Optional[Token]:
        if token.token_type == TokenType.PUNCT:
            return None
        return token

# Preprocessing function for removing url
class RemoveURLsPreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_URLS

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        if token.token_type == TokenType.URL:
            return None
        return token

# Preprocessing function for removing time
class RemoveTimePreprocessor(TokenPreprocessor):
    type = PreprocessType.REMOVE_TIME

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        if token.token_type == TokenType.TIME:
            return None
        return token

# Preprocessing function for Lemmatization
class LematizationPreprocessor(TokenPreprocessor):
    type = PreprocessType.LEMMATIZATION

    morph = majka.Majka('preprocessing/dictionary/majka.w-lt')

    # Majka settings

    # morph.flags |= majka.ADD_DIACRITICS # find word forms with diacritics
    # morph.flags |= majka.DISALLOW_LOWERCASE # do not enable to find lowercase variants
    # morph.flags |= majka.IGNORE_CASE # ignore the word case completely
    morph.flags = 0  # unset all flags

    morph.tags = False  # return just the lemma, do not process the tags
    # morph.tags = True # turn tag processing back on (default)

    # morph.compact_tag = True # return tag in compact form (as returned by Majka)
    # morph.compact_tag = False # do not return compact tag (default)

    morph.first_only = True  # return only the first entry
    # morph.first_only = False # return all entries (default)

    morph.negative = "ne"  # return negative instead of "-"

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        result = self.morph.find(token.processed_form)

        if len(result) == 0:
            return token
        else:
            token.processed_form = result[0]['lemma']
            return token


# Preprocessing function for Stemming
class StemmingPreprocessor(TokenPreprocessor):
    type = PreprocessType.STEMMING

    def preprocess(self, token: Token, document: str) -> Optional[Token]:
        token.processed_form = czech_stemmer.cz_stem_word(token.processed_form)
        return token

# Preprocessing Pipeline Class
class PreprocessingPipeline:
    def __init__(self, preprocessors: list[TokenPreprocessor]):
        self.preprocessors = preprocessors

    def preprocess(self, tokens: list[Token], document: str) -> list[Token]:
        for preprocessor in self.preprocessors:
            tokens = preprocessor.preprocess_all(tokens, document)

        return tokens
