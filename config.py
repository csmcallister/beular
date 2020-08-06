import os

from dotenv import load_dotenv
import joblib

basedir = os.path.abspath(os.path.dirname(__file__))
model_path = os.path.join(
    basedir,
    'app',
    'bin',
    'SGDClassifier-model.joblib'
)
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    ESTIMATOR = joblib.load(model_path)
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


    WTF_CSRF_ENABLED = False
    REDIS_URL = "redis://redis:6379/0"
    QUEUES = ["default"]