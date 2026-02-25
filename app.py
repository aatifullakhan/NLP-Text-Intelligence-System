import streamlit as st
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer

# UI Settings
st.set_page_config(page_title="NLP Text Intelligence System", layout="wide")

# Sidebar
st.sidebar.title("NLP Text Intelligence System")
st.sidebar.write("Created by Aatif 🚀")

# Main UI
st.title("🧠 NLP Text Intelligence System")
st.write("Analyze text sentiment, keywords, and statistics")

text = st.text_area("✍️ Enter your text here", height=200)

if st.button("Analyze Text"):
    if text.strip() == "":
        st.warning("Please enter some text!")
    else:
        # Sentiment Analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0:
            sentiment = "Positive 😊"
        elif polarity < 0:
            sentiment = "Negative 😡"
        else:
            sentiment = "Neutral 😐"

        # Word Count
        words = text.split()
        word_count = len(words)

        # Keyword Extraction
        vectorizer = CountVectorizer(stop_words="english")
        X = vectorizer.fit_transform([text])
        keywords = vectorizer.get_feature_names_out()

        # Display Results
        st.subheader("🔍 Analysis Results")
        st.write(f"**Sentiment:** {sentiment}")
        st.write(f"**Polarity Score:** {polarity}")
        st.write(f"**Word Count:** {word_count}")
        st.write("**Keywords:**")
        st.write(", ".join(keywords))

        st.success("Analysis Completed!")