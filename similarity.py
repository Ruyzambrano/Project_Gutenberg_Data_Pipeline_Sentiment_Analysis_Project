import numpy as np
import matplotlib.pyplot as plt

class SimilarityChecker:
    def __init__(self, books):
        self.books = books
        self.similarity_matrix = np.zeros((len(books), len(books)))

    def calculate_similarity(self, book1, book2):
        # Calculate similarity scores for corresponding sentences
        sentence_similarity_scores = [
            first_sentence.similarity(second_sentence)
            for first_sentence, second_sentence in zip(book1.doc.sents, book2.doc.sents)
        ]

        # Get average similarity between the sentences
        average_similarity = sum(sentence_similarity_scores) / len(sentence_similarity_scores)
        return average_similarity

    def calculate_all_similarities(self):
        for i in range(len(self.books)):
            for j in range(len(self.books)):
                similarity_score = self.calculate_similarity(self.books[i], self.books[j])
                self.similarity_matrix[i, j] = similarity_score

    def display_matrix(self):
        plt.figure(figsize=(8, 6))
        plt.imshow(self.similarity_matrix, cmap='tab20c', interpolation='nearest')
        plt.colorbar()
        plt.xticks(range(len(self.books)), [book.title for book in self.books], rotation=90)
        plt.yticks(range(len(self.books)), [book.title for book in self.books])
        plt.title("Novel Similarity Matrix")
        plt.show()
