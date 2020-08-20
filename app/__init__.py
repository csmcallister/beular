import logging
from logging.handlers import RotatingFileHandler
import os
from os import path

from flask import Flask, render_template
import nltk

try:
    nltk.data.find('wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

from config import Config


def page_not_found(e):  # pragma: no cover
    return render_template('errors/404.html'), 404


def internal_server_error(e):  # pragma: no cover
    return render_template('errors/500.html'), 500


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
        
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    app.shell_context_processor({"app": app})

    if not app.debug and not app.testing:  # pragma: no cover        
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        
        else:
            if not path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/beular.log',
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')

    return app