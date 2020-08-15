from flask import Blueprint

bp = Blueprint('main', __name__)


@bp.after_app_request
def after_request(response):
    """Cache Bust
    """
    cache_cont = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Cache-Control"] = cache_cont
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


from app.main import routes  # noqa: F401