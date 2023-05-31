import re
import os
import requests
import gutenbergpy.textget
from gutenberg_cleaner import simple_cleaner

class BookImporter:
    def get_book(book_id, title):
        """
        Retrieves the text of a book from Project Gutenberg using its book ID,
        cleans the text, and saves it to a file.

        Args:
            book_id (int): The ID of the book on Project Gutenberg.
            title (str): The title of the book.

        Returns:
            str: The file path where the book text is saved.
        """

        #  Get the book from Gutenberg
        raw_book = gutenbergpy.textget.get_text_by_id(book_id)
        
        # Make sure the encoding is uniform
        book_text = raw_book.decode("UTF-8")

        # Remove the metadata using simple_cleaner
        clean_book = simple_cleaner(book_text)

        # Do extra cleaning
        clean_book = re.sub(r"\[Transcriber.*?\]", "", clean_book, flags=re.DOTALL)
        
        # Remove extra newlines and markers for italicised text 
        clean_book = clean_book.strip().replace("_", "").replace("\n", "")

        # Generate a filepath for the txt file
        file_path = "data/{}.txt".format(title.replace(" ", "_"))
        
        # If the file doesn't exist, write the txt file to file_path
        if not os.path.isfile(file_path):
            BookImporter.write_to_file(file_path, clean_book)
        return file_path

    def write_to_file(file_path, book_text):
        """
        Writes the book text to a file.

        Args:
            file_path (str): The file path where the book text will be saved.
            book_text (str): The text content of the book.
        """

        # Write the book to a txt file
        with open(file_path, "w", encoding="UTF-8") as file:
            file.write(book_text)

    def gutendex(book_title, author):
        """
        Searches for a book on the Gutendex API using the book title and author,
        retrieves the book ID, and downloads the book text.

        Args:
            book_title (str): The title of the book.
            author (str): The author of the book.

        Returns:
            tuple: A tuple containing the file path where the book text is saved and the book ID.
        """

        # Set the file_path to None
        file_path, book_id = None, 0

        # Encode the string to fit into a url format
        author = author.replace(" ", "%20")
        book_name = book_title.replace(' ', '%20')

        # Make a GET request to Gutendex
        response = requests.get(f"http://gutendex.com/books/?search={book_name}%20{author}",
                                timeout=10)
        
        # If it works
        if response.status_code == 200:

            # Retrieve the GutenbergID
            book_data = response.json()

            # The GET returns the number of responses found on Gutenberg
            if book_data["count"] != 0:
                book_id = book_data["results"][0]["id"]

                # Get the book if it exists
                file_path = BookImporter.get_book(book_id, book_title)
        
        # Let the user know if the GET fails
        else:
            print(response.status_code)

        return file_path, book_id
