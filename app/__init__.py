import os
from flask import Flask
from dotenv import load_dotenv
from .db import init_db, db_session, Base   # ← usa nosso db.py
from .models import Base as ModelsBase      # se você usa Base em models, ok

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config["SITE_NAME"] = os.getenv("SITE_NAME", "Mangará – Núcleo Agroecológico")
    app.config["BRAND_EMOJI"] = os.getenv("BRAND_EMOJI", "").strip()
    app.config["INSTAGRAM_URL"] = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/horteires_ifsp/")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
    app.config["DEBUG"] = bool(int(os.getenv("FLASK_DEBUG", "0")))

    init_db(app)

    # cria tabelas no banco apontado por DATABASE_URL
    from .models import Base as ModelsBase  # garante import dos models
    ModelsBase.metadata.create_all(bind=db_session.bind)

    from .auth import auth_bp, login_manager
    login_manager.init_app(app)
    app.register_blueprint(auth_bp)

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .ai import ai_bp
    app.register_blueprint(ai_bp)

    @app.context_processor
    def inject_brand():
        return dict(
            SITE_NAME=app.config["SITE_NAME"],
            BRAND_EMOJI=app.config["BRAND_EMOJI"],
            INSTAGRAM_URL=app.config["INSTAGRAM_URL"],
        )

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
