# Project Gutenberg Data Pipeline Sentiment Analysis Project

## Description

This project is designed to analyze books using natural language processing (NLP) techniques. It retrieves a list of books from Goodreads, imports them into a SQLite database, and then performs various analyses on the text of the books.

## Prerequisites

The following packages are required to run the project:

- pandas
- spacy
- sqlite3
- sqlalchemy
- spacytextblob

## Installation

1. Clone the repository to your local machine.
2. Install the required packages using pip:

   ```
   pip install pandas spacy sqlite3 sqlalchemy spacytextblob
   ```
   
3. Download the language model for the spaCy library:

   ```
   python -m spacy download en_core_web_lg
   ```

## Usage

1. Run the `main.ipynb` file.
2. The script will retrieve a list of books from Goodreads and import them into a SQLite database.
3. The script will then perform various analyses on the books, including splitting the books into chapters, performing NLP on the text, and generating sentiment analysis using TextBlob.
4. The analysis results will be printed to the console.

## Project Structure

- `main.py`: The main script to run the project.
- `main.ipynb`: A Jupyter Notebook Version of the project.
- `book_importer.py`: Contains functions for importing books from Project Gutenberg and saving them to files.
- `language_analysis.py`: Defines the `Book` class and contains functions for analyzing the text of the books.
- `similarity.py`: Contains a class for comparing the similarity between books.
- `databases/`: Contains the SQLite database file and the CSV file for storing book data.
- `data/`: Contains the text files for the books.

## Note:

In order to do the analysis, you must find the chapter markers manually using regex expressions first before running the analysis methods.
## Contributing

Contributions to this project are welcome. You can contribute by opening an issue to report a bug or suggest an enhancement, or by submitting a pull request with your own improvements to the codebase.

I am particularly open to creating a way to automate finding the chapter markers for the novels.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
