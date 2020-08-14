# BEULAR

Binarization of End User License Agreement Regression (BEULAR) - a Python Flask application that provides a UI for a supervised machine learning model that can identify problematic clauses in End User License Agreements.

## Getting Started

## Config

Create a `.env` file to set some app-specific environment variables. For example

```ini
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=somethingSuperSecret!
```

Note that if you'd like to be able to push validated predictions and user feedback to the AWS S3 bucket created in the `beular-api` project, you must also add the following to your `.env` file:

```ini
AWS_ACCESS_KEY_ID=123
AWS_SECRET_ACCESS_KEY=456
AWS_DEFAULT_REGION=region-name
```

And you can select which model to use by adjusting the following line in `config.py`:

```python
model_path = os.path.join(
    basedir,
    'app',
    'bin',
    'sgd.joblib' # change this for a different model
)
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
