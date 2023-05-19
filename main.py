import pandas as pd
import spacy
from book_importer import BookImporter



book_id = [43, 345, 41445, 209, 1513]
book_data = []
for book in book_id:
    title, author, text = BookImporter.get_book(book)
    book_data.append({'Title': title, 'Author': author, 'Text': text})



gothic_data = pd.DataFrame(book_data)
gothic_data.info()


print(gothic_data)


nlp = spacy.load('en_core_web_lg')


jekyll_hyde_doc = nlp(jekyll_hyde)
jekyll_hyde_vectors = [token.vector for token in jekyll_hyde_doc]


dracula_doc = nlp(dracula)
dracula_vectors = [token.vector for token in dracula_doc]


frankenstein_doc = nlp(frankenstein)
frankenstein_vectors = [token.vector for token in frankenstein_doc]


turn_of_the_screw_doc = nlp(turn_of_the_screw)
turn_of_the_screw_vectors = [token.vector for token in turn_of_the_screw_doc]


romeo_and_juliet_doc = nlp(romeo_and_juliet)
romeo_and_juliet_vectors = [token.vector for token in romeo_and_juliet_doc]


dracula_jekyll_similarity = dracula_doc.similarity(jekyll_hyde_doc)
print(dracula_jekyll_similarity)


romeo_dracula_similarity = dracula_doc.similarity(romeo_and_juliet_doc)
print(romeo_dracula_similarity)


