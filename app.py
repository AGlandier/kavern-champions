from flask import Flask
from config.settings import Config
from controllers.battleroom_controller import battleroom_bp
from controllers.user_controller import user_bp
from controllers.auth_controller import auth_bp
from database.db import init_db


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init DB
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(battleroom_bp, url_prefix="/battleroom")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
