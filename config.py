import os

from dotenv import load_dotenv
import fasttext
import joblib
import numpy as np

basedir = os.path.abspath(os.path.dirname(__file__))
model_path = os.path.join(
    basedir,
    'estimators',
    'sgd.joblib'  # change this for a different model
)
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    MODEL_URI = os.environ.get('MODEL_URI')
    
    if not os.environ.get('WORKER'):
        if model_path.endswith('bin'):
            estimator = fasttext.load_model(model_path)
            ESTIMATOR = estimator
            MEAN_VEC = np.load(
                os.path.join(
                    basedir,
                    'estimators',
                    'mean_pos_sample_tfidf_vec.npy'
                )
            )
            BT = True
        else:
            if not MODEL_URI:
                ESTIMATOR = joblib.load(model_path)
            BT = False
    
    LOG_TO_STDOUT = True
    FLASK_ENV = os.environ.get('FLASK_ENV')
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    try:
        os.mkdir(UPLOAD_FOLDER)
    except FileExistsError:
        pass
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # REDIS
    # WTF_CSRF_ENABLED = False
    REDIS_URL = "redis://redis:6379/0"
    QUEUES = ["default"]