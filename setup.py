from setuptools import find_packages, setup

setup(
    name='beular',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'contractions==0.0.25',
        'eli5==0.10.1',
        'ipython==7.16.1',
        'joblib==0.16.0',
        'Flask==1.1.1',
        'matplotlib>=3.2.2',
        'nltk==3.5',
        'pandas>=1.0.5',
        'python-dotenv==0.13.0',
        'requests==2.23.0',
        'scikit-learn==0.21.3',
        'textract==1.6.3'
    ],
)