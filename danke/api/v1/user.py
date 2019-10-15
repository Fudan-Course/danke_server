from flask_restplus import Namespace, Resource, fields, reqparse
from danke import settings
from danke.core.render import Render
from danke.database.user import User as UserModel

api = Namespace('users', description='用户数据相关操作')


@api.route('/')
class Users(Resource):
    UsersDataItem = api.model('UsersDataItem', {
        'username': fields.String(required=True, description='用户名'),
        'email': fields.String(required=True, description='邮箱')
    })
    UsersRsp = api.model('UsersRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.List(fields.Nested(UsersDataItem))
    })

    def do_get_users(self):
        try:
            users = UserModel.query.all()
        except Exception as e:
            return 1, e.message, None
        return 0, '成功', users

    # TODO 这个API应该加上分页，筛选和排序(用parser)，并设置权限
    @api.doc('get_users')  # 起到id的作用，用于帮助理解
    @api.marshal_with(UsersRsp)  # 通过marshal，可以自动将其中对应的项返回，其他项不返回
    def get(self):
        '''获取用户列表'''
        err_code, message, data = self.do_get_users()
        return Render.common_response(err_code, message, data), 200


@api.route('/<id>')
@api.param('id', '用户id')
class User(Resource):
    # 获取用户资料应该使用profile
    # 获取用户数据 TODO 删除本API
    UserData = api.model('UserData', {
        'id': fields.Integer(required=True),
        'username': fields.String(),
        'email': fields.String(),
        'password': fields.String()
    })
    UserRsp = api.model('UserRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.Nested(UserData)
    })

    def do_get_user(self, id):
        user = None
        try:
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                return 1, '用户不存在', None
        except Exception as e:
            return 9, e.message, None
        return 0, '成功', user

    @api.doc('get_user_profile')
    @api.marshal_with(UserRsp)
    def get(self, id):
        '''通过id获取用户数据'''
        err_code, message, data = self.do_get_user(id)
        return Render.common_response(err_code, message, data), 200
