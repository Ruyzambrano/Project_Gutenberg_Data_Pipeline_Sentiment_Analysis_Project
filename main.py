# %%
import pandas as pd
import spacy
import sqlite3
from sqlalchemy import create_engine

from spacytextblob.spacytextblob import SpacyTextBlob

from goodreads_book_scraper import get_listopia
from book_importer import BookImporter
from language_analysis import Book
from similarity import SimilarityChecker


# %% [markdown]
# # Data Pipeline

# %% [markdown]
# ## Get a list of books from GoodReads

# %%

# Get the URL from the GoodReads website
best_books_ever_url = 'https://www.goodreads.com/list/show/1.Best_Books_Ever'
large_book_list_url = 'https://www.goodreads.com/list/show/952.1001_Books_You_Must_Read_Before_You_Die'
this_week_url = 'https://www.goodreads.com/book/most_read'

# Scrape the website and return lists of books, authors and average review
goodreads_list, author_list, review_list = get_listopia(this_week_url)



# %%
# Empty book_data list to store the books in
book_data = []

# Iterate through the book list and check if it is on Gutenberg
for count, book in enumerate(goodreads_list):
    file_path, book_id = BookImporter.gutendex(book, author_list[count])
    
    # Store the book in the book list
    book_data.append({'GutenbergID': book_id, 'Title': book, 'Author': author_list[count], 'Review': review_list[count], 'FilePath': file_path})


# %%
# Convert the book list into a pandas and check for missing values
book_data = pd.DataFrame(book_data)
book_data.info()

# %% [markdown]
# ### Remove Duplicates (if any)

# %%
# Check for duplicates
duplicates = book_data.duplicated()

duplicate_rows = book_data[duplicates]
print(duplicate_rows)

# %%
# If there are any duplicate values (check by title and author), remove them
book_data = book_data.drop_duplicates(subset=['Title', 'Author'], keep='first')

# %%
# Check the dataframe
print(book_data.head())

# %%
# Get a list of unique author names
author_list = book_data['Author'].unique()
author_list_df = pd.DataFrame({'Name': author_list})

print(author_list_df)

# %% [markdown]
# ## Add data to SQL database

# %% [markdown]
# ### Start up SQL

# %%
# Start the SQL database 
conn = sqlite3.connect('databases/book_repository.db')
cursor = conn.cursor()
engine = create_engine('sqlite:///databases/book_repository.db')


# %% [markdown]
# ### Create the tables (Commented out after the first iteration)

# %%
# Create Authors table
with engine.begin() as connection:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Authors(
            AuthorID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR
        )
    ''')

# %%
# Create Gutenberg table
with engine.begin() as connection:
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Gutenberg(
        GutenbergID INTEGER PRIMARY KEY,
        FilePath VARCHAR
        );
    ''')
        # If there is not GutenbergID, it will reference this
    conn.execute('''
        INSERT OR IGNORE INTO Gutenberg (GutenbergID, FilePath)
        VALUES (0, 'Not Available')
        ''')

# %%
# Create Books table
with engine.begin() as connection:
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Books(
        GutenbergID VARCHAR(7),
        Title VARCHAR,
        AuthorID INTEGER,
        Review DOUBLE,
        FOREIGN KEY (GutenbergID) REFERENCES Gutenberg(GutenbergID)
        FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
        );
''')


# %% [markdown]
# ### Put the data in a temporary table

# %%
# Turn the books data into a temporary SQL table
book_data.to_sql('temp_books', conn, if_exists='replace', index=False)

# %%
# Turn the author list into a temporary SQL table
author_list_df.to_sql('temp_authors', conn, if_exists='replace', index=False)

# %%
# Insert the author names into the table, ignore repetitions
with engine.begin() as connection:
    conn.execute("""
        INSERT INTO Authors (Name)
        SELECT DISTINCT LOWER(t.Name)
        FROM temp_authors AS t
        LEFT JOIN Authors AS a ON LOWER(t.Name) = LOWER(a.Name)
        WHERE a.Name IS NULL
    """)

# %%
with engine.begin() as connection:
    conn.execute('''
        INSERT INTO Gutenberg (GutenbergID, FilePath)
        SELECT t.GutenbergID, t.FilePath
        FROM temp_books as t
        LEFT JOIN Gutenberg AS g ON t.GutenbergID = g.GutenbergID
        WHERE t.FilePath IS NOT NULL
          AND (g.GutenbergID IS NULL OR g.GutenbergID = 0)
    ''')

# %%
# Insert the rest of the Book data, with the foreign keys
with engine.begin() as connection:
    conn.execute('''
        INSERT INTO Books (GutenbergID, Title, AuthorID, Review)
        SELECT t.GutenbergID, t.Title, a.AuthorID, t.Review
        FROM temp_books AS t
        LEFT JOIN Authors AS a ON LOWER(t.Author) = LOWER(a.Name)
        LEFT JOIN Books AS b ON t.GutenbergID = b.GutenbergID
        WHERE b.GutenbergID IS NULL
    ''')

# %% [markdown]
# ### Drop the temporary Table

# %%
# Drop the temporary tables
with engine.begin() as connection:
    conn.execute("DROP TABLE IF EXISTS temp_books")
    conn.execute('DROP TABLE IF EXISTS temp_authors')


# %%
# Check to see if the Data was inserted correctly
cursor.execute('''
    SELECT Books.Title, Authors.Name, Books.GutenbergID
    FROM Books
    LEFT OUTER JOIN Authors ON Books.AuthorID = Authors.AuthorID
''')

rows = cursor.fetchall()
for row in rows:
    print(f'{row[0]}: {row[1]}, {row[2]}')
print(len(rows))


# %%
# Check if the Gutenberg table was inserted correctly
cursor.execute('SELECT * FROM Gutenberg')

rows = cursor.fetchall()
for row in rows:
    print(f'{row[0]:>7}: {row[1]}')
print(len(rows))

# %%
cursor.execute('SELECT * FROM Gutenberg WHERE GutenbergID=0')
print(cursor.fetchall())

# %% [markdown]
# ## Commit any unsaved changes

# %%
conn.commit()

# %%
# Stop the SQL server
conn.close()

# %% [markdown]
# # Analysis

# %% [markdown]
# ## Load the NLP and add TextBlob to it

# %%
# Load the large dataset and add the TextBlob pipeline
nlp = spacy.load('en_core_web_lg')
nlp.add_pipe('spacytextblob')

# Create a books list to store the Book objects
books = []

# %% [markdown]
# ## Read the files and analyse the novels

# %% [markdown]
# ### Jekyll and Hyde

# %%
# Import Jekyll and Hyde from Gutenberg
BookImporter.get_book(43, 'Jekyll and Hyde')

# Read the txt file and create a Book object
with open('data\Jekyll_and_Hyde.txt', 'r', encoding='UTF-8') as file:
    jekyll_hyde = Book('Jekyll and Hyde', file.read())

# Denote the chapter markers in a regex expression
chapter_markers = r'((\nSTORY OF THE DOOR)|(\nSEARCH FOR MR. HYDE)|(\nDR. JEKYLL WAS QUITE AT EASE)|(\nTHE CAREW MURDER CASE)|(\nINCIDENT OF THE LETTER)|(\nINCIDENT OF DR. LANYON)|(\nINCIDENT AT THE WINDOW)|(\nTHE LAST NIGHT)|(\nDR. LANYON’S NARRATIVE)|(\nHENRY JEKYLL’S FULL STATEMENT OF THE CASE))'


# %%
# Split the book into chapters
jekyll_hyde.split_into_chapters(chapter_markers)


# %%
# Conduct NLP analysis sentence by sentence
jekyll_hyde.do_nlp(nlp)


# %%
# Do NLP on each chapter
jekyll_hyde.chapter_nlp(nlp)


# %%
# Show sentiment analysis of the entire text
jekyll_hyde.blobify()

# %%
# Show the analysis of the book
jekyll_hyde.get_analysis()

# %%
# Show the sentiment analysis by chapter
jekyll_hyde.chapter_analysis()


# %%
# Add the book to the book object list
books.append(jekyll_hyde)

# %% [markdown]
# ### Dracula

# %%
with open('data\Dracula.txt', 'r', encoding='UTF-8') as file:
    dracula = Book('Dracula', file.read())
chapter_markers = r'(PREFACE.)|(LETTER I+\.)|(CHAPTER [IVXLCDM]+\n)'



# %%
dracula.split_into_chapters(chapter_markers)


# %%
dracula.do_nlp(nlp)


# %%
dracula.chapter_nlp(nlp)


# %%
dracula.blobify()

# %%
dracula.get_analysis()


# %%
dracula.chapter_analysis()
books.append(dracula)

# %% [markdown]
# ### Frankenstein

# %%
BookImporter.get_book(84, 'Frankenstein')
with open('data\Frankenstein.txt', 'r', encoding='UTF-8') as file:
    frankenstein = Book('Frankenstein', file.read())

chapter_markers = r'\n((Letter .)|(Chapter .+))'
frankenstein.split_into_chapters(chapter_markers)


# %%
frankenstein.do_nlp(nlp)


# %%
frankenstein.chapter_nlp(nlp)


# %%
frankenstein.blobify()


# %%
frankenstein.get_analysis()


# %%
frankenstein.chapter_analysis()
books.append(frankenstein)

# %% [markdown]
# ### The Turn of the Screw

# %%
BookImporter.get_book(209, 'The Turn of the Screw')
with open('data\The_Turn_of_the_Screw.txt', 'r', encoding='UTF-8') as file:
    turn_of_the_screw = Book('The Turn of the Screw', file.read())

chapter_markers = r'((\nI\n)|(\nII)|(\nIII)|(\nIV)|(\nV)|(\nVI)|(\nVII)|(\nVIII)|(\nIX)|(\nX)|(\nXI)|(\nXII)|(\nXIII)|(\nXIV)|(\nXV)|(\nXVI)|(\nXVII)|(\nXVIII)|(\nXIX)|(\nXX)|(\nXXI)|(\nXXII)|(\nXXIII)|(\nXXIV))'


# %%
turn_of_the_screw.split_into_chapters(chapter_markers)


# %%
turn_of_the_screw.do_nlp(nlp)


# %%
turn_of_the_screw.chapter_nlp(nlp)


# %%
turn_of_the_screw.blobify()


# %%
turn_of_the_screw.get_analysis()


# %%
turn_of_the_screw.chapter_analysis()
books.append(turn_of_the_screw)

# %% [markdown]
# ### Romeo and Juliet

# %%
BookImporter.get_book(1513, 'Romeo and Juliet')
with open('data\Romeo_and_Juliet.txt', 'r', encoding='UTF-8') as file:
    romeo_and_juliet = Book('Romeo and Juliet', file.read())

chapter_markers = r'(THE PROLOGUE\n)|(SCENE I. A public place)|(SCENE II. A Street)|(SCENE III. Room in Capulet’s House)|(SCENE IV. A Street)|(SCENE V. A Hall in Capulet’s House)|(ACT II\n\n)|(SCENE I. An open place adjoining Capulet’s Garden)|(SCENE II. Capulet’s Garden)|(SCENE III. Friar Lawrence’s Cell)|(SCENE IV. A Street)|(SCENE V. Capulet’s Garden)|(SCENE VI. Friar Lawrence’s Cell)|(SCENE I. A public Place)|(SCENE II. A Room in Capulet’s House)|(SCENE III. Friar Lawrence’s cell)|(SCENE IV. A Room in Capulet’s House)|(SCENE V. An open Gallery to Juliet’s Chamber, overlooking the Garden)|(SCENE I. Friar Lawrence’s Cell)|(SCENE II. Hall in Capulet’s House)|(SCENE III. Juliet’s Chamber)|(SCENE IV. Hall in Capulet’s House)|(SCENE V. Juliet’s Chamber; Juliet on the bed)|(SCENE I. Mantua. A Street)|(SCENE II. Friar Lawrence’s Cell)|(SCENE III. A churchyard; in it a Monument belonging to the Capulets)'


# %%
romeo_and_juliet.split_into_chapters(chapter_markers)


# %%
romeo_and_juliet.do_nlp(nlp)


# %%
romeo_and_juliet.chapter_nlp(nlp)


# %%
romeo_and_juliet.blobify()


# %%
romeo_and_juliet.get_analysis()


# %%
romeo_and_juliet.chapter_analysis()
books.append(romeo_and_juliet)

# %% [markdown]
# ### Alice's Adventures in Wonderland

# %%
BookImporter.get_book(11, 'Alice’s Adventures in Wonderland')
with open('data\Alice’s_Adventures_in_Wonderland.txt', 'r', encoding='UTF-8') as file:
    alice = Book('Alice in Wonderland', file.read())
chapter_markers = r'(CHAPTER I.\nDown the Rabbit-Hole)|(CHAPTER II.\nThe Pool of Tears)|(CHAPTER III.\nA Caucus-Race and a Long Tale)|(CHAPTER IV.\nThe Rabbit Sends in a Little Bill)|(CHAPTER V.\nAdvice from a Caterpillar)|(CHAPTER VI.\nPig and Pepper)|(CHAPTER VII.\nA Mad Tea-Party)|(CHAPTER VIII.\nThe Queen’s Croquet-Ground)|(CHAPTER IX.\nThe Mock Turtle’s Story)|(CHAPTER X.\nThe Lobster Quadrille)|(CHAPTER XI.\nWho Stole the Tarts\?)|(CHAPTER XII.\nAlice’s Evidence)'


# %%
alice.split_into_chapters(chapter_markers)


# %%
alice.do_nlp(nlp)


# %%
alice.chapter_nlp(nlp)


# %%
alice.blobify()


# %%
alice.get_analysis()


# %%
alice.chapter_analysis()
books.append(alice)

# %% [markdown]
# ### The War of the Worlds

# %%
BookImporter.get_book(36, 'War of the Worlds')
with open('data\War_of_the_Worlds.txt', 'r', encoding='UTF-8') as file:
    war_of_the_worlds = Book('War of the Worlds', file.read())

chapter_markers = r'\n[IVX]+\.\n'


# %%
war_of_the_worlds.split_into_chapters(chapter_markers)


# %%
war_of_the_worlds.do_nlp(nlp)


# %%
war_of_the_worlds.chapter_nlp(nlp)


# %%
war_of_the_worlds.blobify()


# %%
war_of_the_worlds.get_analysis()


# %%
war_of_the_worlds.chapter_analysis()
books.append(war_of_the_worlds)

# %% [markdown]
# ### Wuthering Heights

# %%
with open('data\Wuthering_Heights.txt', 'r', encoding='UTF-8') as file:
    wuthering_heights = Book('Wuthering Heights', file.read())

chapter_markers = r'CHAPTER [IVX]+'


# %%
wuthering_heights.split_into_chapters(chapter_markers)


# %%
wuthering_heights.do_nlp(nlp)


# %%
wuthering_heights.chapter_nlp(nlp)


# %%
wuthering_heights.blobify()


# %%
wuthering_heights.get_analysis()


# %%
wuthering_heights.chapter_analysis()
books.append(wuthering_heights)

# %% [markdown]
# ### Pride and Prejudice

# %%
with open('data\Pride_and_Prejudice.txt', 'r', encoding='UTF-8') as file:
    pride_prejudice = Book('Pride and Prejudice', file.read())

chapter_markers = r'(Chapter I\.\])|CHAPTER [IVXL]+\.'


# %%
pride_prejudice.split_into_chapters(chapter_markers)

# %%
pride_prejudice.do_nlp(nlp)

# %%
pride_prejudice.chapter_nlp(nlp)

# %%
pride_prejudice.get_analysis()


# %%
pride_prejudice.chapter_analysis()
books.append(pride_prejudice)

# %% [markdown]
# ### Moby Dick

# %%
with open('data\Moby-Dick_or,_the_Whale.txt', 'r', encoding='UTF-8') as file:
    moby_dick = Book('Moby Dick', file.read())


# %%
chapter_markers = r'(\nCHAPTER .+)|(\nEPILOGUE.)'

# %%

moby_dick.split_into_chapters(chapter_markers)


# %%
moby_dick.do_nlp(nlp, 10000)


# %%
moby_dick.chapter_nlp(nlp)


# %%
moby_dick.blobify()


# %%
moby_dick.get_analysis()


# %%
moby_dick.chapter_analysis()
books.append(moby_dick)

# %% [markdown]
# ### Ulysses

# %%
BookImporter.get_book(4300, 'Ulysses')
with open('data\\Ulysses.txt', 'r', encoding='UTF-8') as file:
    ulysses = Book('Ulysses', file.read())


# %%
chapter_markers = r''
for i in range(1, 18):
    chapter_markers += r'(\n\[ {} \])|'.format(i)
chapter_markers += r'(\n\[ 18 \])'

# %%

ulysses.split_into_chapters(chapter_markers)


# %%
ulysses.do_nlp(nlp, 10000)


# %%
ulysses.chapter_nlp(nlp)


# %%
ulysses.blobify()


# %%

ulysses.get_analysis()


# %%
ulysses.chapter_analysis()
books.append(ulysses)

# %% [markdown]
# ### A Christmas Carol

# %%
with open('data\A_Christmas_Carol.txt', 'r', encoding='UTF-8') as file:
    christmas_carol = Book('A Christmas Carol', file.read())

# %%
chapter_markers = r'STAVE (.+)'

# %%
christmas_carol.split_into_chapters(chapter_markers)

# %%
christmas_carol.do_nlp(nlp)

# %%
christmas_carol.chapter_nlp(nlp)

# %%
christmas_carol.blobify()

# %%
christmas_carol.get_analysis()

# %%
christmas_carol.chapter_analysis()
books.append(christmas_carol)

# %% [markdown]
# ## Dorian Grey

# %%
with open('data\The_Picture_of_Dorian_Gray.txt', 'r', encoding='UTF-8') as file:
    dorian_gray = Book('The Picture of Dorian Gray', file.read())


# %%
chapter_markers = r'\n(CHAPTER .+)'

# %%
dorian_gray.split_into_chapters(chapter_markers)

# %%
dorian_gray.do_nlp(nlp)

# %%
dorian_gray.chapter_nlp(nlp)

# %%
dorian_gray.blobify()

# %%
dorian_gray.get_analysis()

# %%
dorian_gray.chapter_analysis()
books.append(dorian_gray)

# %% [markdown]
# ## War and Peace

# %%
with open('data\War_and_Peace.txt', 'r', encoding='UTF-8') as file:
    war_and_peace = Book('War and Peace', file.read())


# %%
chapter_markers = r'\nCHAPTER [IXVC]+\n'

# %%
war_and_peace.split_into_chapters(chapter_markers)

# %%
war_and_peace.do_nlp(nlp)

# %%
war_and_peace.chapter_nlp(nlp)

# %%
war_and_peace.blobify()

# %%
war_and_peace.get_analysis()

# %%
war_and_peace.chapter_analysis()
books.append(war_and_peace)

# %% [markdown]
# ## The Odyssey

# %%
with open('data\The_Odyssey.txt', 'r', encoding='UTF-8') as file:
    
    # Remove the footnotes
    book_text = file.read().split('FOOTNOTES')[1]
    odyssey = Book('The Odyssey', book_text)

chapter_markers = r'\nBOOK .+'

# %%
odyssey.split_into_chapters(chapter_markers)

# %%
odyssey.do_nlp(nlp)

# %%
odyssey.chapter_nlp(nlp)

# %%
odyssey.blobify()

# %%
odyssey.get_analysis()

# %%
odyssey.chapter_analysis()
books.append(odyssey)

# %% [markdown]
# ## Conduct similarity analysis and display results

# %%
# Do a similarity analysis between each book in the books list
checker = SimilarityChecker(books)
checker.calculate_all_similarities()


# %%
# Show the results of the similarity analysis
checker.display_matrix()


