from textblob import TextBlob
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

string = '''I was told that this road is in summertime
excellent, but that it had not yet been put in order after the winter
snows.'''

nlp = spacy.load('en_core_web_lg')
nlp.add_pipe('spacytextblob')

spaced = nlp(string)

for assessment in spaced._.assessments:
    tokens = ', '.join(assessment[0])  # Join the tokens into a single string
    polarity = assessment[1]
    subjectivity = assessment[2]
    
    print(f'\tTokens: {tokens}')
    print(f'\t\tPolarity: {polarity}')
    print(f'\t\tSubjectivity: {subjectivity}\n')
