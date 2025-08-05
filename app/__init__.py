import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# define NIST function codes, display names, and header colors
FUNCTION_DEFS = [
    ("GV", "Govern", "#F8F1C8"),
    ("ID", "Identify", "#4DB2E6"),
    ("PR", "Protect", "#C079D6"),
    ("DE", "Detect", "#FDBE5A"),
    ("RS", "Respond", "#D9241F"),
    ("RC", "Recover", "#82CF6B"),
]


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # configure the database to live in instance/nist_tracker.db
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'nist_tracker.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    # Load instance/config.py
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    # Initialize Flask Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to continue."

    # then register your blueprints (as before)…
    from app.blueprints.auth       import auth_bp
    from app.blueprints.dashboard  import bp as dashboard_bp
    from app.blueprints.systems    import bp as systems_bp
    from app.blueprints.mappings   import bp as mappings_bp
    from app.blueprints.functions  import bp as functions_bp
    from app.blueprints.priorities import bp as priorities_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(systems_bp)
    app.register_blueprint(mappings_bp)
    app.register_blueprint(functions_bp)
    app.register_blueprint(priorities_bp)

    @app.context_processor
    def inject_nist_functions():
        funcs = [code for code, _, _ in FUNCTION_DEFS]
        name_map = {code: name for code, name, _ in FUNCTION_DEFS}
        function_colors = {code: color for code, _, color in FUNCTION_DEFS}
        return dict(funcs=funcs, name_map=name_map, function_colors=function_colors)

    return app
