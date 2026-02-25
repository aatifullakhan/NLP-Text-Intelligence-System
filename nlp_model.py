import spacy
import nltk
import re
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob

# downloads
nltk.download('stopwords')
nltk.download('vader_lexicon')

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

# Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

# TF-IDF Keywords
def extract_keywords_tfidf(text):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out()

# Sentiment
def get_sentiment(text):
    return sia.polarity_scores(text)

# Summarization (simple)
def summarize_text(text):
    blob = TextBlob(text)
    return blob.noun_phrases[:5]

# Readability
def text_stats(text):
    words = len(text.split())
    sentences = len(text.split('.'))
    return words, sentences