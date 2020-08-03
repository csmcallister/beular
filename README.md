# BEULAR

Binarization of End User License Agreement Regression (BEULAR) - a Python Flask application that provides a UI for a supervised machine learning model that can identify problematic clauses in End User License Agreements.

## Getting Started

## Config

Create a `.env` file to set some app-specific environment variables. For example

```
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY="somethingSuperSecret!"
```

## Build

We recommend using Docker since the `textract` dependency can be tricky to install, especially on Windows:

```bash
docker-compose up --build
```

## Run the Tests

This will verify that everything is working as expected:

```bash
coverage run -m pytest
```

It will also let you see the test coverage with:

```bash
coverage report
```

## TODO

- make sure document clause's are split properly upon upload (check pdfs)
- For clauses that are less than three words, ensure modal notes the pred override
- implement feedback callback to submit to s3
