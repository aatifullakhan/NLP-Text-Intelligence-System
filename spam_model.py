from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Dummy training data (you can improve)
texts = ["free money win", "hello friend how are you", "win lottery now", "meeting tomorrow"]
labels = [1,0,1,0]  # 1 spam, 0 ham

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

def predict_spam(text):
    X_test = vectorizer.transform([text])
    return model.predict(X_test)[0]