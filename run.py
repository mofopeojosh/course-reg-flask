import os

from app import create_app

basedir = os.path.abspath(os.path.dirname(__file__))
config_name = os.getenv('APP_SETTINGS') # config_name = "development"

app = create_app(config_name)


if __name__ == '__main__':
    app.run()
