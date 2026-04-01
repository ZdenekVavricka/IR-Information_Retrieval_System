# IR-Semestral project

This semestral project implements an Information Retrieval (IR) system that processes data in the Czech language in either **json** or **jsonl** format. The system allows for **Vector** or **Boolean** searching within the indexed data.

## Execution
The program can be started either using the command:

`python.exe main.py`

or by importing the project into the PyCharm IDE and running `main.py`.

### Libraries
For the application to function correctly, the following libraries must be installed:

- `lxml`
- `majka`
- `numpy`
- `tkinter`
- `unidecode`

## GUI
The IR system features a graphical user interface that allows users to add their own data and index it. Subsequently, it is possible to search the indexed data using Vector or Boolean search. You can also limit the number of shown results using **Results to display**. If the number of results to display is set to **0**, the application will print all found results.

## Evaluation Script
The application also implements an interface for an evaluation script. Evaluation can be initiated using the `-test` parameter:

`python.exe main.py -test`

The evaluation script then indexes the evaluation data from the `../data/cs/` folder and creates a results file in the `../output/ranked_results_yyyy-mm-dd_hh-mm-ss.txt` folder.

The output file serves as one of the inputs for the `trec-eval` evaluation script. The other required file is `gold_relevancies.txt`, which is part of the evaluation data.

### Evaluation Results
The table below lists the evaluation results with different types of preprocessing:

| Preprocessing | Indexing (s) | TF-IDF (s) | Boolean (s) | MAP |
| ----------- | ----------- | ----------- | ----------- | ----------- | 
| Lemmatization | 163.84 | 38.13 | 81.38 | 0.1727 |
| Stemming | 171.12 | 31.88 | 70.05 | 0.1624 |
| Lemmatization,<br>Remove diacritics,<br>Lowercase | 197.42 | 37.46 | 81.37 | 0.1733 |
| Stemming,<br>Remove diacritics,<br>Lowercase | 202.08 | 32.94 | 66.29 | 0.1846 |

The best **MAP score (0.1846)** was achieved using Stemming with diacritics removal and conversion to lowercase. This high result was achieved only after adding article titles to the documents.

In terms of operation time, Lemmatization had the fastest indexing. Vector search was fastest with standalone Stemming, and the fastest Boolean search was achieved with Stemming combined with diacritics removal and lowercase conversion.

Regarding the time results, these are largely influenced by the load on the machine where the evaluation is running.

## Log File
The IR system also generates a `log.txt` file, which can be found in the `../log/` folder. This file contains a record of the console output from the GUI or the output of the evaluation script.

## Input and Evaluation Data
Input and evaluation data are available here: [data](https://drive.google.com/file/d/1eDDk8K1ET7f9CnhkzjhYrUpySjR_Xqkg/view?usp=sharing)

After downloading and extracting the zip file, simply copy the `data.jsonl` file and the `cs` folder into the `data` directory.
