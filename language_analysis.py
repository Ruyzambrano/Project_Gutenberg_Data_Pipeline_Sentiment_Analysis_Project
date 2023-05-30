import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import spacy
import re
from spacytextblob.spacytextblob import SpacyTextBlob
from scipy import stats
from transformers import pipeline
from textblob import TextBlob

class Book:
    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.chapters = []
        self.chapter_titles = []
        self.chapter_docs = []
        self.lemma = []
        self.doc = None
        self.stop = None
        self.vectors = None
        self.polarity = None
        self.subjectivity = None
        self.blob_polarity = None
        self.blob_subjectivity = None

    def do_nlp(self, nlp_creator, batch_size=None):
        if batch_size:
            self.doc = self._process_large_text(nlp_creator, batch_size)
        else:
            try:
                self.doc = nlp_creator(self.text)
            except Exception:
                self.do_nlp(nlp_creator, 10000)
        self.stop = [token for token in self.doc if not token.is_stop]
        self.vectors = [token.vector for token in self.doc]
        self.polarity = self.doc._.polarity
        self.subjectivity = self.doc._.subjectivity
        self.lemma = [token.lemma_ for token in self.doc if not token.is_stop]

    def _process_large_text(self, nlp, batch_size):
        batches = [self.text[i:i + batch_size] for i in range(0, len(self.text), batch_size)]
        docs = []
        polarity = []
        subjectivity = []
        for batch in batches:
            doc = nlp(batch)
            docs.append(doc)
            polarity.append(doc._.polarity)
            subjectivity.append(doc._.subjectivity)
        return spacy.tokens.Doc(nlp.vocab).from_docs(docs)

    def get_analysis(self):
        # Basic Statistics
        total_tokens = len(self.doc)
        unique_words = self.lemma
        average_sentence_length = total_tokens / len(list(self.doc.sents))

        highest_polarity = ''
        highest_score = 0
        lowest_polarity = ''
        lowest_score = 0
        polarity_score = []
        subjectivity_score = []
        for sent in self.doc.sents:
            polarity = sent._.polarity
            polarity_score.append(polarity)
            subjectivity = sent._.subjectivity
            subjectivity_score.append(subjectivity)
            if polarity > highest_score:
                highest_sent = sent
                highest_polarity = sent.text
                highest_score = polarity
            if polarity < lowest_score:
                lowest_sent = sent
                lowest_score = polarity
                lowest_polarity = sent.text

        self.polarity = np.mean(polarity_score)
        self.subjectivity = np.mean(subjectivity_score)

        print(f'Basic Statistics for {self.title}:')
        print(f'\tTotal Tokens:\t\t\t{total_tokens}')
        print(f'\tUnique Words:\t\t\t{len(unique_words)}')
        print(f'\tAverage Sentence Length:\t{average_sentence_length}')
        print(f'\tAverage Sentence Polarity:\t{self.polarity}')
        print(f'\tAverage Sentence Subjectivity:\t{self.subjectivity}\n')
        print(f'Sentence with highest polarity ({highest_score}):\n{highest_polarity}\n')
        for assessment in highest_sent._.assessments:
            tokens = ', '.join(assessment[0])
            polarity = assessment[1]
            subjectivity = assessment[2]
            print(f'\tTokens: {tokens}')
            print(f'\t\tPolarity: {polarity}')
            print(f'\t\tSubjectivity: {subjectivity}\n')
        print(f'Sentence with lowest polarity ({lowest_score}):\n{lowest_polarity}\n')
        for assessment in lowest_sent._.assessments:
            tokens = ', '.join(assessment[0])
            polarity = assessment[1]
            subjectivity = assessment[2]
            print(f'\tTokens: {tokens}')
            print(f'\t\tPolarity: {polarity}')
            print(f'\t\tSubjectivity: {subjectivity}\n')

        # Sentiment Analysis
        sentiment_scores = []
        for sentence in self.doc.sents:
            sentence_polarity = sentence._.polarity
            sentiment_scores.append(sentence_polarity)

        mean_sentiment = np.mean(sentiment_scores)
        median_sentiment = np.median(sentiment_scores)

        # Plot sentiment scores
        plt.figure(figsize=(10, 6))
        plt.plot(sentiment_scores)
        plt.axhline(y=mean_sentiment, color='r', linestyle='--', label='Mean')
        plt.axhline(y=median_sentiment, color='g', linestyle='--', label='Median')
        plt.xlabel('Sentence')
        plt.ylabel('Sentiment Polarity')
        plt.title(f'Sentiment Analysis for sentences in "{self.title}"')
        plt.show()

        # Word Frequency Analysis
        word_freq = {}
        for token in unique_words:
            word = token.capitalize()
            if word.isalnum() and len(word) > 1:
                if word not in word_freq:
                    word_freq[word] = 1
                else:
                    word_freq[word] += 1

        # Convert word frequency dictionary to a DataFrame for easier manipulation
        word_freq_df = pd.DataFrame.from_dict(word_freq, orient='index', columns=['Frequency'])
        word_freq_df = word_freq_df.sort_values(by='Frequency', ascending=False)

        # Plot the top 20 most frequent words
        top_n = 20
        plt.figure(figsize=(10, 6))
        word_freq_df.head(top_n).plot(kind='bar', legend=False)
        plt.xlabel('Word')
        plt.ylabel('Frequency')
        plt.title(f'Top {top_n} Most Frequent Words in "{self.title}"')
        plt.xticks(rotation=45)
        plt.show()

    def blobify(self):
        sentiment = TextBlob(self.text)
        
        self.blob_polarity = sentiment.sentiment[0]
        self.blob_subjectivity = sentiment.sentiment[1]     

        print(f'Blobby Statistics for {self.title}')
        print(f'Whole Text Polarity:\t\t\t{self.blob_polarity}')
        print(f'Whole Text Subjectivity:\t\t{self.blob_subjectivity}\n')

    def chapter_nlp(self, nlp_creator):
        for chapter in self.chapters:
            doc = nlp_creator(chapter)
            self.chapter_docs.append(doc)
    
    def split_into_chapters(self, chapter_markers):
        chapters_text = self.text
        chapters_text = re.split(chapter_markers, chapters_text)
        chapters_text.pop(0)
        for chapter in chapters_text:
            if chapter:
                if len(chapter) > 100:
                    self.chapters.append(chapter)
        print(f'Number of chapters: {len(self.chapters)}')
        self.chapter_titles = re.findall(chapter_markers, self.text)
    
    def chapter_analysis(self):
        sentiment_score = []

        highest_chapter_polarity = -1
        lowest_chapter_polarity = 1
        for count, chapter in enumerate(self.chapter_docs, 1):
            sentiment_score.append(chapter._.polarity)
            if chapter._.polarity > highest_chapter_polarity:
                highest_chapter_polarity = chapter._.polarity
                highest_chapter = chapter
                highest_count = count
            if chapter._.polarity < lowest_chapter_polarity:
                lowest_chapter_polarity = chapter._.polarity
                lowest_chapter = chapter
                lowest_count = count

        mean_sentiment = np.mean(sentiment_score)
        median_sentiment = np.median(sentiment_score)
        print(f'Median Sentiment: {median_sentiment}')

        # Plot sentiment scores
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(sentiment_score)), sentiment_score)
        plt.axhline(y=mean_sentiment, color='r', linestyle='--', label='Mean')
        plt.axhline(y=median_sentiment, color='g', linestyle='--', label='Median')
        plt.xlabel('Chapter')
        plt.ylabel('Sentiment Polarity')
        plt.title(f'Sentiment Analysis for Chapters in "{self.title}"')
        plt.show()

        print(f'The most positive chapter was Chapter {highest_count}: {highest_chapter._.polarity}')
        for assessment in highest_chapter._.assessments:
            tokens = ', '.join(assessment[0])
            polarity = assessment[1]
            subjectivity = assessment[2]
            print(f'\tTokens: {tokens}')
            print(f'\t\tPolarity: {polarity}')
            print(f'\t\tSubjectivity: {subjectivity}\n')

        print(f'The most negative chapter was Chapter {lowest_count}: {lowest_chapter._.polarity}')
        for assessment in lowest_chapter._.assessments:
            tokens = ', '.join(assessment[0])
            polarity = assessment[1]
            subjectivity = assessment[2]
            print(f'\tTokens: {tokens}')
            print(f'\t\tPolarity: {polarity}')
            print(f'\t\tSubjectivity: {subjectivity}\n')