from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from backend.config import Config
from backend.extensions import db
from backend.models import User
from backend.routes.admin_routes import admin_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.job_routes import job_bp
from backend.routes.report_routes import report_bp
from backend.routes.resume_routes import resume_bp
from backend.routes.screening_routes import screening_bp
from backend.utils.file_utils import ensure_folder
from backend.utils.logger import configure_logging


def create_app():
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    app = Flask(__name__, static_folder=str(frontend_dir), static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)
    configure_logging(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(screening_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    ensure_folder(app.config["UPLOAD_FOLDER"])
    ensure_folder(app.config["REPORT_FOLDER"])

    with app.app_context():
        db.create_all()
        seed_default_admin(app)

    register_frontend_routes(app, frontend_dir)
    register_error_handlers(app)
    return app


def seed_default_admin(app):
    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        return
    admin = User(
        name=app.config["DEFAULT_ADMIN_NAME"],
        email=app.config["DEFAULT_ADMIN_EMAIL"],
        role="admin",
        status="active",
    )
    admin.set_password(app.config["DEFAULT_ADMIN_PASSWORD"])
    db.session.add(admin)
    db.session.commit()
    app.logger.info("Default admin created: %s", admin.email)


def register_frontend_routes(app: Flask, frontend_dir: Path) -> None:
    @app.get("/")
    def root():
        return send_from_directory(frontend_dir, "index.html")

    @app.get("/<path:path>")
    def frontend_files(path: str):
        requested = frontend_dir / path
        if requested.exists() and requested.is_file():
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, "index.html")


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(413)
    def file_too_large(_error):
        return jsonify({"success": False, "message": "File size exceeds the allowed limit"}), 413

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Resource not found"}), 404
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"success": False, "message": "Internal server error"}), 500


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
