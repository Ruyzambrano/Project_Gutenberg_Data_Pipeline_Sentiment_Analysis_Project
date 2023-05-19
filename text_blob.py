from textblob import TextBlob

class Blobify:
    def __init__(self, text):
        self.text = text
        self.blob = TextBlob(text)
