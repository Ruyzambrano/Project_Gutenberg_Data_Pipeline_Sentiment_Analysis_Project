import pandas as pd
from book_importer import BookImporter

jekyll_hyde = BookImporter.get_book(43, 'jekyll_hyde')
dracula = BookImporter.get_book(345, 'dracula')
frankenstein = BookImporter.get_book(41445, 'frankenstein')
turn_of_the_screw = BookImporter.get_book(209, 'turn_of_the_screw')

book_data = [
    {'Author': 'Robert Louis Stevenson', 'Title': 'The Strange Case of Dr. Jekyll and Mr. Hyde', 'Published': '1886-01-05', 'Text': jekyll_hyde},
    {'Author': 'Bram Stoker', 'Title': 'Dracula', 'Published': '1897-05-26', 'Text': dracula},
    {'Author': 'Mary Shelley', 'Title': 'Frankenstein; or, The Modern Promethius', 'Published': '1818-01-01', 'Text': frankenstein},
    {'Author': 'Henry James', 'Title': 'The Turn of the Screw', 'Published': '1898-10-01', 'Text': turn_of_the_screw},
]
gothic_data = pd.DataFrame(book_data)
gothic_data['Published'] = pd.to_datetime(gothic_data['Published'])
gothic_data.info()
