import gutenbergpy.textget
from gutenberg_cleaner import simple_cleaner
import re

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

        BookImporter.write_to_file(title.replace(' ', '_'), clean_book)
        return title, author, clean_book

    def write_to_file(book_name, book_text):
        with open(f'data/{book_name}.txt', 'w', encoding='UTF-8') as file:
            file.write(book_text)


book_id = [43, 345, 41445, 209, 1513]
book_data = []
for book in book_id:
    title, author, text = BookImporter.get_book(book)
    book_data.append({'Title': title, 'Author': author, 'Text': text})
