from flask import Blueprint

bp = Blueprint(
    "ecowitt",                 # blueprint name
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/plugin/ecowitt",   # optional: URLs für plugin views/static (views optional)
    static_url_path="/static",  # optional, verhindert static collisions
)

def register(app, ctx=None) -> None:
    """
    Called by signaldeck-core to register this plugin.
    ctx is optional here; blueprint registration doesn't need it.
    """
    app.register_blueprint(bp)
