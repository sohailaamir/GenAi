
# ---- Build a lightweight image for Streamlit + LangChain ----
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install OS deps (uncomment graphviz if you want PNG diagrams in-container)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    # graphviz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
# Streamlit server entrypoint
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
