FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# TextBlob / NLTK tokenizers used by medical_utils
RUN python -c "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('punkt', quiet=True)"

COPY . .

ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

EXPOSE 8501

# Render and similar pass PORT; default 8501 for local Docker
CMD sh -c 'streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}'
