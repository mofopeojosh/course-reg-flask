from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_cors import CORS, cross_origin

# local import
from instance.config import app_config
from flask import request, jsonify, abort, render_template, redirect

# initialize sql-alchemy
db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()
cors = CORS()

from app.models import Student, Staff

def create_app(config_name):
  
  app = FlaskAPI(__name__, 
            static_folder = "../dist/static",
            template_folder = "../dist",
            instance_relative_config=True)
  app.config.from_object(app_config[config_name])
  app.config.from_pyfile('config.py')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


  db.init_app(app)
  ma.init_app(app)
  login_manager.init_app(app)
  

  @app.route('/', defaults={'path': ''})
  @app.route('/<path:path>')
  def catch_all(path):
      return render_template("index.html")

  @app.errorhandler(404)
  def page_not_found(error):
    return render_template("404.html"), 404

  

  from app.controller import api

  app.register_blueprint(api)
  CORS(app, resources={r"/api/*": {"origin": "http://127.0.0.1:8080"}}, supports_credentials=True)

  return app
