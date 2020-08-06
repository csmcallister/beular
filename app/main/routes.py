import os

from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template, 
    request
)
import redis
from rq import Queue, Connection
from werkzeug.utils import secure_filename

from app.main import bp
from app.tasks import create_task
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
        txt_file = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        with open(txt_file, 'w') as txt:
            txt.write(text)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
        return render_template('scan.html', filename=f.filename)
    else:
        flash('Allowed document types are pdf, doc and docx')
        return redirect(request.url)


@bp.route('/to_s3', methods=['POST'])
def to_s3():
    feedback = request.form["type"]
    
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        task = q.enqueue(create_task, feedback)
    
    response_object = {
        "status": "success",
        "data": {
            "task_id": task.get_id()
        }
    }
    
    return jsonify(response_object), 202
