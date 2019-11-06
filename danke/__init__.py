from flask import Flask
from flask_cors import CORS
from flask_mail import Mail

from danke.settings import settings
from danke.database import db
from danke.core.mailer import mailer
from .api.v1 import blueprint as apiv1
# from .api.v2 import blueprint as apiv2

app = Flask(__name__)
CORS(app, supports_credentials=True)


def configure_app(flask_app):
    for k, v in settings.items():
        flask_app.config[k] = v
        print(k, v)


configure_app(app)


def initialize_app(flask_app):
    configure_app(flask_app)
    # init
    db.init_app(flask_app)
    mailer.init_app(flask_app)
    # apis
    app.register_blueprint(apiv1)


def run_server():
    initialize_app(app)
    # log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=settings['FLASK_DEBUG'])
