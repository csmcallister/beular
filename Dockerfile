FROM python:3.7

COPY . .

RUN pip install -e .

RUN pip install gunicorn

RUN apt-get update && apt-get install -y \
    antiword \
    build-essential \
    ca-certificates \
    ffmpeg \
    gcc \
    gzip \
    lame \
    #libav-tools \
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
    ssh \
    swig \
    tar \
    unrtf \
    zlib1g-dev \
    #clean up the apt cache
    && rm -rf /var/lib/apt/lists/*

RUN python -W ignore -m nltk.downloader punkt
RUN python -W ignore -m nltk.downloader averaged_perceptron_tagger
RUN python -W ignore -m nltk.downloader wordnet

ENV FLASK_APP main.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 1

EXPOSE 5000

CMD gunicorn -w 2 -t 180 -b :5000 main:app