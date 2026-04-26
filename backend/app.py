from flask import Flask
from flask_cors import CORS
from config.settings import Config
from controllers.battleroom_controller import battleroom_bp
from controllers.user_controller import user_bp
from controllers.auth_controller import auth_bp
from database.db import init_db
from extensions import socketio


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"),
        async_mode="eventlet",
    )

    # Init DB
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(battleroom_bp, url_prefix="/battleroom")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Swagger UI — uniquement en mode développement
    if app.config.get("DEBUG"):
        from flasgger import Swagger
        from swagger.spec import SWAGGER_TEMPLATE
        Swagger(app, template=SWAGGER_TEMPLATE)

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000)
