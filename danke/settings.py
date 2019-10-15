# -*- coding: utf-8 -*-
# Flask settings
FLASK_SERVER_NAME = '127.0.0.1:8811'
FLASK_DEBUG = True  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False  # 禁用swagger自带的帮助信息

# SQLAlchemy settings
# SQLALCHEMY_TRACK_DATABASE_URI = 'mysql+pymysql://username:password@localhost/db_name'
SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlite.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
