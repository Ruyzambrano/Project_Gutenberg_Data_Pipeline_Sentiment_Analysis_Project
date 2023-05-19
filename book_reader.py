class BookReader:

    def read_book(extension):
        with open(extension, 'r', encoding='UTF-8') as file:
            book = file.read()
        return book