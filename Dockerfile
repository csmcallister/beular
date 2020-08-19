FROM python:3.7

RUN apt-get update && apt-get install -y \
    antiword \
    build-essential \
    ca-certificates \
    ffmpeg \
    flac \
    gcc \
    gzip \
    lame \
    libmad0 \
    libpq-dev \
    libpulse-dev \
    libsox-fmt-mp3 \
    libxml2-dev \
    libxslt1-dev \
    make \
    musl-dev \
    poppler-utils \
    python-dev \
    sox \
    ssh \
    sudo \
    swig \
    tar \
    tesseract-ocr \
    unrtf \
    zlib1g-dev \
    #clean up the apt cache
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN python -W ignore -m nltk.downloader punkt
RUN python -W ignore -m nltk.downloader averaged_perceptron_tagger
RUN python -W ignore -m nltk.downloader wordnet

ENV FLASK_APP main.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 1

COPY estimators/ ./estimators/
COPY models/ ./models/
COPY config.py main.py manage.py ./
COPY app/ ./app/
