import requests
from bs4 import BeautifulSoup

def get_listopia(url):
    response = requests.get(url)
    book_list = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        book_title_element = soup.find_all('span', itemprop='name')
        for item in book_title_element:
            book_list.append(item.text)
    else:
        print(response.status_code)

    return book_list