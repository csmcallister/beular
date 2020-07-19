from flask import Blueprint, current_app, redirect, request

bp = Blueprint('main', __name__)


@bp.after_app_request
def after_request(response):
    """Cache Bust
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#@bp.before_app_request
#def before_request():
#    scheme = request.headers.get('X-Forwarded-Proto')
#    if scheme and scheme == 'http' and request.url.startswith('http://'):
#        url = request.url.replace('http://', 'https://', 1)
#        return redirect(url, code=301)


from app.main import routes  # noqa: F401