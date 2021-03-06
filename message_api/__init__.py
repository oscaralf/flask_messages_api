from flask import Flask

from config import app_config


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(app_config[config_name])
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise Exception("Environment variable SQLALCHEMY_DATABASE_URI must be defined")

    from flask_restful import Api
    api = Api(app)
    setattr(app, 'api', api)

    with app.app_context():
        api.init_app(app)
        from . import sqlalquemy_store
        from . import routes
        from . import healthcheck_routes

        return app
