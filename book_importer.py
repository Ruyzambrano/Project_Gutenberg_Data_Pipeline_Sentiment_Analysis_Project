import gutenbergpy.textget
from gutenberg_cleaner import simple_cleaner
import re
import os
import requests
from goodreads_book_scraper import get_listopia


class BookImporter:
    def get_book(book_id):
        raw_book = gutenbergpy.textget.get_text_by_id(book_id)
        book_text = raw_book.decode('UTF-8')

        # Extract title and author using regular expressions
        title_match = re.search(r'title: (.+)', book_text, re.IGNORECASE)
        author_match = re.search(r'author: (.+)', book_text, re.IGNORECASE)

        # Get title and author from the matches
        title = title_match.group(1).strip() if title_match else ''
        author = author_match.group(1).strip() if author_match else ''
        
        # Remove the metadata using simple_cleaner
        clean_book = simple_cleaner(book_text)

        clean_book = re.sub(r'\[Transcriber.*?\]', '', clean_book, flags=re.DOTALL)
        clean_book = clean_book.strip().replace('_', '').replace('\n', '')
        file_path = 'data/{}.txt'.format(title.replace(' ', '_'))
        if not os.path.isfile(file_path):
            file_path = BookImporter.write_to_file(file_path, clean_book)
        return title, author, clean_book, file_path

    def write_to_file(book_name, book_text):
        file_path = f'data/{book_name}.txt'
        with open(file_path, 'w', encoding='UTF-8') as file:
            file.write(book_text)
        return file_path
    def gutendex(book_title):
        title, author, text, file_path = None, None, None, None
        response = requests.get(f'http://gutendex.com/books/?search={book_title}')
        if response.status_code == 200:
            book_data = response.json()
            if book_data['count'] != 0:
                book_id = book_data['results'][0]['id']
                title, author, text, file_path = BookImporter.get_book(book_id)
        return title, author, text, file_path
