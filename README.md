# IR-semestralni_prace

Semestrální práce realizuje Information Retrieval systém (IR), který zpracovává data v Českém jazyce a ve formátu json nebo jsonl. Dále tento systém umožňuje Vektorové nebo Booleovské vyhledávání v zaindexovaných datech.

## Spuštění
Program je možné spustit buď pomocí příkazu

`python.exe main.py`

nebo naimportováním projektu do PyCharm IDE a spuštěním `main.py`.

### Knihovny
Pro správné fungování aplikace je nutné mít nainstalované tyto knihovny:

- `lxml`
- `majka`
- `numpy`
- `tkinter`
- `unidecode`

## GUI
IR systém má grafické rozhraní, které umožňuje přidání vlastních dat a jejich zaindexování. Následně je možné v zaindexovaných datech vyhledávat pomocí Vektorového nebo Boolovského vyhledávání. Je zde také možné omezit počet zobrazovaných výsledků pomocí **Results to display**. Pokud je počet zobrazovaných výsledků nastaven na hodnotu **0**. Aplikace vypíše všechny nalezené výsledky.   

## Evaulační script
Aplikace také implementuje rozhraní pro evaluační script. Evaulaci je možné spustit pomocí parametru `-test`:

`python.exe main.py -test`

Evaulační script poté zaindexuje evaulační data ze složky `../data/cs/` a vytvoří soubor s výsledky do složky `../output/ranked_results_yyyy-mm-dd_hh-mm-ss.txt`.

Výstupní soubor slouží jako jeden ze vstupů pro evaluační script `trec-eval`. Dalším potřebným souborem je soubor `gold_relevancies.txt`, který je součástí evaulačních dat

### Výsledky evaulace
V tabulce jsou uvedeny výsledky evaulace s různým preprocessingem:

| Preprocessing | Indexace (s) | TF-IDF (s) | Boolean (s) | MAP |
| ----------- | ----------- | ----------- | ----------- | ----------- | 
| Lemmatization | 163.84 | 38.13 | 81.38 | 0.1727 |
| Stemming | 171.12 | 31.88 | 70.05 | 0.1624 |
| Lemmatization,<br>Remove diacritics,<br>Lowercase | 197.42 | 37.46 | 81.37 | 0.1733 |
| Stemming,<br>Remove diacritics,<br>Lowercase | 202.08 | 32.94 | 66.29 | 0.1846 |

Nejlepší skóre **MAP (0.1846)** má Stemming s odtraněním diakritiky a převedením na malá písmena.
Takto vysokého výsledku se mi podařilo dosáhnout až po přidání titulků článků do dokumentů.

Pokud bychom hodnotili podle času jednotlivých operací tak nejrychlejší indexaci měla Lemmatizace.
Vektorové vyhledávání bylo nejryhlejší u samotného Stemmingu a nejrychlejší Booleovské vyhledávání bylo u Stemmingu s odtraněním diakritiky a převedením na malá písmena.

Co se týče časových výsledků tak ty jsou do značné míry ovlivněny zatížením stroje na kterém běží evaluace.

## Log soubor
IR systém také generuje `log.txt`, který lze nalézt ve složce `../log/`. Tento soubor obsahuje záznam výstupu do konzole v GUI nebo výstup evaulačního scriptu. 

## Vstupní a Evaluační data
Vstupní data a evaluační data jsou dostupná zde: [data](https://drive.google.com/file/d/1eDDk8K1ET7f9CnhkzjhYrUpySjR_Xqkg/view?usp=sharing)

Po stažení a rozbalení zip souboru stačí nakopírovat soubor `data.jsonl` a složku `cs` do složky `data`.
