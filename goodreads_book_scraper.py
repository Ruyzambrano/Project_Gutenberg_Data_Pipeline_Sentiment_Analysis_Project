import re
import requests
from bs4 import BeautifulSoup


def get_listopia(url):
    """
    Scrapes book information from a Goodreads Listopia page.

    Args:
        url (str): The URL of the Listopia page.

    Returns:
        tuple: A tuple containing lists of book titles, authors, and reviews.
    """

    # Make a GET request to GoodReads
    response = requests.get(url, timeout=10)

    # Lists for storing the book information
    book_list = []
    author_list = []
    reviews = []

    # If the GET request works
    if response.status_code == 200:

        # Parse the raw data
        soup = BeautifulSoup(response.text, "html.parser")

        # Analyse the HTML to find the book titles, authors and average reviews
        book_elements = soup.find_all("a", class_="bookTitle")
        author_elements = soup.find_all("a", class_="authorName")
        review_elements = soup.find_all("span", class_="minirating")

        # Clean the raw data a bit more
        for book_element, author_element, review_element in zip(
            book_elements, author_elements, review_elements
        ):
            # Strip the text of leading, trailing whitespace
            book_info = book_element.text.strip()

            # Add the tite to the list
            book_list.append(book_info)

            # Strip the author name of whitespace
            author_info = author_element.text.strip()

            # Add author to the list
            author_list.append(author_info)

            # Remove extra elements from the average review
            review_text = review_element.get_text(strip=True)

            # Extract only the review
            average_rating = re.search(r"(\d+\.\d+)", review_text)
            if average_rating:
                reviews.append(average_rating.group(1))
            else:
                reviews.append(None)

    # If it didn't work, let the user know
    else:
        print(response.status_code)

    return book_list, author_list, reviews
