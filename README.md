# BEULAR

Binarization of End User License Agreement Regression (BEULAR) - a Python Flask application that provides a UI for a supervised machine learning model that can identify problematic clauses in End User License Agreements.

## Getting Started

We recommend the following docker setup since the `textract` dependency can be tricky to install, especially on Windows. But for local dev it's useful to install the app as a package with `pip install -e .`

To start the app:

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

 - make sure document clause's are split properly upon upload
 - ignore clause's that are just a few words
 - see why the eli5 explanation is only for the first positive clause
 - Shorten training in SageMaker

## Data Issues
 - A lot of the training data is single words or phrases
 - Data is imbalanced
 - Some positive instances don't make sense:
    - COPYING, INSTALLING OR USING
    - Sales Order Form
    - Appendix  B – Online Tutoring Pricing