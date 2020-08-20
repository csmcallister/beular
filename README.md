# BEULAR

Binarization of End User License Agreement Recommendations (BEULAR) - a Python Flask application that provides a UI for supervised machine learning models that can identify problematic clauses in End User License Agreements. Models come pre-packaged, but the config can be updated to use a REST API deployed on AWS (see [this project](https://github.com/csmcallister/beular-api) for details).

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

If you'd like to be able to push validated predictions and user feedback to the AWS S3 bucket created in the [beular-api project](https://github.com/csmcallister/beular-api), you must also add the following to your `.env` file:

```ini
AWS_ACCESS_KEY_ID=123
AWS_SECRET_ACCESS_KEY=456
AWS_DEFAULT_REGION=region-name
BUCKET=bucket-name
```

And if you'd like to use a model you deployed behind a REST API in AWS using the [beular-api project](https://github.com/csmcallister/beular-api), you need to additionally set the uri for that api in your .env file:

```ini
MODEL_URI="https://your-aws-api.com/predict
```

>Note that if you're using the BlazingText model, you still need a local copy of the model (i.e. model.bin) and you should specify this model in the config as well. Read the next section to see how to download the model.

### Model Selection

You can choose from the following models:

- BlazingText - model.bin (you must download this file from [here](https://drive.google.com/file/d/16EG0Zfj-ChdzM_R_W9cBKEHxpcNYMSku/view?usp=sharing) since it's over 1GB in size)
- Logistic Regression - sgd.joblib
- Gradient Boosting Classifier - gbc.joblib
- Random Forest Classifier - rfc.joblib

>Note that the BlazingText model is very large, so be sure you've got enough memory on your machine for it to load.

You can select which model to use by adjusting the following lines in `config.py`:

```python
model_path = os.path.join(
    basedir,
    'app',
    'bin',
    'sgd.joblib' # change this for a different model
)
```

And then be sure to remove that model's entry in the .dockerignore file. If using the BlazingText model, be sure to also remove the *.npy entry.

## Build

We recommend using Docker since the `textract` dependency can be tricky to install, especially on Windows:

```bash
docker-compose up --build
```

>You're going to need several GB of disk space for this.

Once the build is complete, go to `http://localhost:5000/` to see the app!

## Run the Tests

This will verify that everything is working as expected:

```bash
python -m coverage run -m pytest
```

It will also let you see the test coverage with:

```bash
python -m coverage report
```

## Deployment

This app can been deployed to Heroku so long as you choose a beefy performance dyno that can handle multiple docs at once, especially if you're deploying a model to run inside the container instead of via an API. But first, change the Dockerfile by adding the following line at the end:

```Dockerfile
CMD gunicorn -t 2400 -b 0.0.0.0:$PORT main:app
```

Log in to Container Registry:

```bash
heroku container:login
```

Create the app:

```bash
heroku create
```

Build the image and push to Container Registry:

```bash
heroku container:push web
```

Then release the image to the app:

```bash
heroku container:release web
```

Finally, open the app:

```bash
heroku open
```
