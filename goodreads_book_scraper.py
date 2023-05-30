import requests
import re
from bs4 import BeautifulSoup

def get_listopia(url):
    response = requests.get(url)
    book_list = []
    author_list = []
    reviews = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        book_elements = soup.find_all('a', class_='bookTitle')
        author_elements = soup.find_all('a', class_='authorName')
        review_elements = soup.find_all('span', class_='minirating')

        for book_element, author_element, review_element in zip(book_elements, author_elements, review_elements):
            book_info = book_element.text.strip()
            book_list.append(book_info)
            author_info = author_element.text.strip()
            author_list.append(author_info)
            review_text = review_element.get_text(strip=True)
            average_rating = re.search(r'(\d+\.\d+)', review_text)
            if average_rating:
                reviews.append(average_rating.group(1))
            else:
                reviews.append(None)

    else:
        print(response.status_code)

    return book_list, author_list, reviews
