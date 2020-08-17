# BEULAR

Binarization of End User License Agreement Regression (BEULAR) - a Python Flask application that provides a UI for supervised machine learning models that can identify problematic clauses in End User License Agreements.

## Getting Started

## Config

Create a `.env` file to set some app-specific environment variables. For example, a bare minimum setup:

```ini
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=somethingSuperSecret!
```

### AWS Integration

If you'd like to be able to push validated predictions and user feedback to the AWS S3 bucket created in the `beular-api` project, you must also add the following to your `.env` file:

```ini
AWS_ACCESS_KEY_ID=123
AWS_SECRET_ACCESS_KEY=456
AWS_DEFAULT_REGION=region-name
```

And if you'd like to use a model you deployed behind a REST API in AWS using the [beular-api project](https://github.com/csmcallister/beular-api), you need to additionally set the uri for that api in your .env file:

```ini
MODEL_URI="https://your-aws-api.com/predict
```

>Note that if you're using the BlazingText model, you also need a local copy of the model (i.e. model.bin) and you should specify this model in the config as well.

### Model Selection

And you can select which model to use by adjusting the following line in `config.py`:

```python
model_path = os.path.join(
    basedir,
    'app',
    'bin',
    'sgd.joblib' # change this for a different model
)
```

You can choose from the following models:

- BlazingText - model.bin (you must download this file from [here](https://drive.google.com/file/d/1G-oWjBq5iuD6N8b7fiaSo-hVhSZ_Z1WE/view?usp=sharing) since it's over 1.2GB in size)
- Logistic Regression - sgd.joblib
- Gradient Boosting Classifier - gbc.joblib
- Random Forest Classifier - rfc.joblib

>Note that the BlazingText model is very large, so be sure you've got enough memory on your machine for it to load

## Build

We recommend using Docker since the `textract` dependency can be tricky to install, especially on Windows:

```bash
docker-compose up --build
```

## Run the Tests

This will verify that everything is working as expected:

```bash
python -m coverage run -m pytest
```

It will also let you see the test coverage with:

```bash
python -m coverage report
```
