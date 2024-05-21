FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader maxent_ne_chunker words punkt averaged_perceptron_tagger

COPY . sandbox_worker/
