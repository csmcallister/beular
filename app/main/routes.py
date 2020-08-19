import glob
import os

from flask import (
    current_app,
    jsonify,
    render_template, 
    request
)
import redis
from rq import Queue, Connection
from werkzeug.utils import secure_filename

from app.main import bp
from app.tasks import create_task
from app import model


def allowed_file(filename):
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@bp.route('/scan', methods=['GET'])
def scan():
    return render_template('scan.html', results=None)


@bp.route('/scan_doc', methods=['POST'])
def scan_doc():
    docs = glob.glob(f"{current_app.config['UPLOAD_FOLDER']}/*.txt")
    doc_names = []
    results = []
    for doc in docs:
        with open(doc, 'r') as f:
            lines = f.readlines()
        _results = model.predict(lines, current_app)
        results.append(_results)
        os.remove(doc)
        doc_name = doc.replace("-", ".").replace(".txt", "")
        doc_names.append(os.path.basename(doc_name))
    
    return render_template('scan.html', results=results, doc_names=doc_names)


@bp.route('/upload_doc', methods=['POST'])
def upload_doc():
    uploaded_files = request.files.getlist('file')
    filenames = []
    for i, f in enumerate(uploaded_files):
        if f and allowed_file(f.filename) and secure_filename(f.filename):
            filenames.append(f.filename)
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                f.filename
            )
            f.save(file_path)
            text = model.read_doc(file_path)
            old_name, old_ext = f.filename.split(".")
            new = f'{old_name}-{old_ext}.txt'
            txt_file = os.path.join(current_app.config['UPLOAD_FOLDER'], new)
            
            with open(txt_file, 'w') as txt:
                txt.write(text)
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass

    return render_template('scan.html', filenames=filenames, results=None)


@bp.route('/to_s3', methods=['POST'])
def to_s3():
    if not os.environ.get('BUCKET'):
        response_object = {
            "status": "error",
            "data": {
                "message": "REDIS_URL not provided to app"
            }
        }
        return jsonify(response_object), 202

    feedback = request.form["type"]
    
    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        q = Queue()
        task = q.enqueue(create_task, feedback)
    
    response_object = {
        "status": "success",
        "data": {
            "task_id": task.get_id()
        }
    }
    
    return jsonify(response_object), 202
