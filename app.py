import streamlit as st
from nlp_model import clean_text, extract_keywords_tfidf, get_sentiment, summarize_text, text_stats
from spam_model import predict_spam
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI NLP Intelligence", page_icon="🧠", layout="wide")

# Sidebar
with st.sidebar:
    menu = option_menu("AI NLP System",
                       ["Home", "Analyzer", "Upload File", "About"],
                       icons=["house","cpu","upload","info"])

# HOME
if menu == "Home":
    st.title("🧠 AI NLP Text Intelligence System")
    st.write("Advanced AI system to analyze text like real products.")
    st.success("Go to Analyzer to start!")

# ANALYZER
if menu == "Analyzer":
    st.header("📝 Enter Text")

    text = st.text_area("Paste your text here", height=200)

    if st.button("Analyze AI"):
        clean = clean_text(text)
        keywords = extract_keywords_tfidf(clean)
        sentiment = get_sentiment(clean)
        summary = summarize_text(text)
        words, sentences = text_stats(text)
        spam = predict_spam(text)

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Words", words)
        col2.metric("Sentences", sentences)
        col3.metric("Sentiment", sentiment["compound"])

        st.subheader("Clean Text")
        st.code(clean)

        st.subheader("Keywords")
        st.write(keywords)

        st.subheader("Summary Keywords")
        st.write(summary)

        # Spam Result
        st.subheader("Spam Detection")
        if spam == 1:
            st.error("🚨 Spam Message Detected")
        else:
            st.success("✅ Not Spam")

        # Sentiment Chart
        st.subheader("Sentiment Chart")
        labels = ["Positive", "Negative", "Neutral"]
        values = [sentiment["pos"], sentiment["neg"], sentiment["neu"]]
        plt.bar(labels, values)
        st.pyplot(plt)

# FILE UPLOAD
if menu == "Upload File":
    st.header("📂 Upload Text File")
    file = st.file_uploader("Upload .txt file", type=["txt"])

    if file:
        content = file.read().decode("utf-8")
        st.text_area("File Content", content, height=300)

# ABOUT
if menu == "About":
    st.header("About Project")
    st.write("""
    AI NLP Text Intelligence System  
    Features:
    - Sentiment Analysis  
    - Keyword Extraction  
    - Summarization  
    - Spam Detection  
    - File Upload  
    - AI Dashboard UI  

    Built by Aatif using Python, NLP, ML, Streamlit.
    """)