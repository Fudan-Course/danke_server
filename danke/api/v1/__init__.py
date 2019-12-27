from flask import Blueprint
from flask_restplus import Api

from .user import api as user_api
from .auth import api as auth_api
from .forum import api as forum_api
from .topic import api as topic_api

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(blueprint,
          title='Danke',
          version='1.0',
          description='Fudan course server api')

api.add_namespace(user_api)
api.add_namespace(auth_api)
api.add_namespace(forum_api)
api.add_namespace(topic_api)
