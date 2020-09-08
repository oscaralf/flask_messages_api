from flask import Flask
from flask_restful import Api
from message_api.sqlalquemy_store import register_app
from config import app_config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise Exception("Environment variable SQLALCHEMY_DATABASE_URI must be defined")
    api = Api(app)
    setattr(app, 'api', api)

    with app.app_context():
        register_app(app)
        from . import routes  # Import routes

        api.init_app(app)

        return app
