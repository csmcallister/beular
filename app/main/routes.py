import os
import time

from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template, 
    Response, 
    request,
    send_from_directory,
    url_for
)
import requests
from werkzeug.utils import secure_filename

from app.main import bp
from app import models


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@bp.route('/scan', methods=['GET'])
def scan():
    return render_template('scan.html')


@bp.route('/scan_doc', methods=['POST'])
def scan_doc():
    doc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'doc.txt')
    with open(doc_path, 'r') as f:
        lines = f.readlines()
    results = models.predict(lines, current_app)
    return render_template('scan.html', results=results)


@bp.route('/upload_doc', methods=['POST'])
def upload_doc():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.url)
    f = request.files['file']
    if f.filename == '':
        flash("No document selected for uploading")
        return redirect(request.url)
    if f and allowed_file(f.filename) and secure_filename(f.filename):
        file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            f.filename
        )
        f.save(file_path)
        text = models.read_doc(file_path)
        filename = 'doc.txt'
        with open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), 'w') as txt:
            txt.write(text)
        os.remove(file_path)
        return render_template('scan.html', filename=filename)
    else:
        flash('Allowed document types are pdf, doc and docx')
        return redirect(request.url)
