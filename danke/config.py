# -*- coding: utf-8 -*-
import os
# Flask settings
# SERVER_NAME = '127.0.0.1:8000' # 域名，用于生成URL，host和port应该在运行时指定
FLASK_DEBUG = True  # Do not use debug mode in production

# Flask-Restplus settings
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
ERROR_404_HELP = False  # 禁用swagger自带的帮助信息

# SQLAlchemy settings
# SQLALCHEMY_TRACK_DATABASE_URI = 'mysql+pymysql://username:password@localhost/db_name'
SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlite.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Mail settings
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('DANKE_MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('DANKE_MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('DANKE_MAIL_USERNAME')
