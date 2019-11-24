import os

from flask import Flask
from flask_cors import CORS
from flask_mail import Mail

from danke import config
from danke.database import db, add_command
from danke.core.mailer import mailer


def initialize_app(app):
    # init
    CORS(app, supports_credentials=True)
    db.init_app(app)
    mailer.init_app(app)
    # add commands
    add_command(app)
    # apis
    from .api.v1 import blueprint as apiv1
    # from .api.v2 import blueprint as apiv2
    app.register_blueprint(apiv1)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    # SECRET_KEY='dev', # user
    # DATABASE=os.path.join(app.instance_path, 'danke.sqlite'),
    # )
    # 加载默认配置
    app.config.from_object(config)
    if test_config is None:
        # 加载用户配置
        app.config.from_pyfile('danke/config.py', silent=True)
    else:
        # 加载测试配置
        app.config.from_mapping(test_config)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    initialize_app(app)

    return app


# def run_server():
#     app = create_app()
#     # log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
#     app.run(debug=settings['FLASK_DEBUG'])
