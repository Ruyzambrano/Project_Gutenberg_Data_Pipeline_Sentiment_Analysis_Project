import gutenbergpy.textget
import gutenbergpy.gutenbergcache
from gutenberg_cleaner import simple_cleaner

class BookImporter:

    def get_book(book_id, book_name):
        raw_book = gutenbergpy.textget.get_text_by_id(book_id)
        clean_book = simple_cleaner(raw_book.decode('UTF-8'))
        BookImporter.write_to_file(book_name, clean_book)
        return clean_book

    def write_to_file(book_name, book_text):
        with open(f'data\{book_name}.txt', 'w', encoding='UTF-8') as file:
            file.write(book_text)
            