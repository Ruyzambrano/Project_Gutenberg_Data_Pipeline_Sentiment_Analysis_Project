import gutenbergpy.textget
from gutenberg_cleaner import simple_cleaner
import re
import os
import requests
from goodreads_book_scraper import get_listopia


class BookImporter:
    def get_book(book_id, title):
        raw_book = gutenbergpy.textget.get_text_by_id(book_id)
        book_text = raw_book.decode('UTF-8')

        # Remove the metadata using simple_cleaner
        clean_book = simple_cleaner(book_text)

        clean_book = re.sub(r'\[Transcriber.*?\]', '', clean_book, flags=re.DOTALL)
        clean_book = clean_book.strip().replace('_', '').replace('\n', '')
        file_path = 'data/{}.txt'.format(title.replace(' ', '_'))
        if not os.path.isfile(file_path):
            BookImporter.write_to_file(file_path, clean_book)
        return file_path

    def write_to_file(file_path, book_text):
        with open(file_path, 'w', encoding='UTF-8') as file:
            file.write(book_text)

    def gutendex(book_title, author):
        file_path, book_id = None, None
        author = author.replace(' ', '%20')
        response = requests.get(f'http://gutendex.com/books/?search={book_title}%20{author}')
        if response.status_code == 200:
            book_data = response.json()
            if book_data['count'] != 0:
                book_id = book_data['results'][0]['id']
                file_path = BookImporter.get_book(book_id, book_title)
        return file_path, book_id
