from flask_restplus import Namespace, Resource, fields, reqparse
from danke import settings
from danke.core.render import Render
from danke.core.tool import *
from danke.database.user import User as UserModel

api = Namespace('users', description='用户数据相关操作')


# @api.route('/')
# class Users(Resource):  # 占位，具体功能有待商榷
#     UsersDataItem = api.model('UsersDataItem', {
#         'username': fields.String(required=True, description='用户名'),
#         'email': fields.String(required=True, description='邮箱')
#     })
#     UsersRsp = api.model('UsersRsp', {
#         'err_code': fields.Integer(required=True),
#         'message': fields.String(),
#         'data': fields.List(fields.Nested(UsersDataItem))
#     })
#     # TODO 这个API应该加上分页，筛选和排序(用parser)，并设置权限
#     @api.doc('get_users')  # 起到id的作用，用于帮助理解
#     @api.marshal_with(UsersRsp)  # 通过marshal，可以自动将其中对应的项返回，其他项不返回
#     def get(self):
#         '''获取用户列表'''
#         err_code, message, data = self.do_get_users()
#         return Render.common_response(err_code, message, data), 200

#     def do_get_users(self):
#         try:
#             users = UserModel.query.all()
#         except Exception as e:
#             return 1, e.message, None
#         return 0, '成功', users


# @api.route('/<user_id>')
# @api.param('user_id', '用户id')
# class User(Resource):  # 占位，这里应该是数据相关的API
#     # 获取用户资料应该使用profile，本API用于调试
#     # 获取用户数据 TODO 删除本API
#     UserData = api.model('UserData', {
#         'id': fields.Integer(required=True),
#         'username': fields.String(),
#         'email': fields.String(),
#         'password': fields.String()
#     })
#     UserRsp = api.model('UserRsp', {
#         'err_code': fields.Integer(required=True),
#         'message': fields.String(),
#         'data': fields.Nested(UserData)
#     })
#     @api.doc('get_user_profile')
#     @api.marshal_with(UserRsp)
#     def get(self, user_id):
#         '''通过id获取用户数据'''
#         err_code, message, data = self.do_get_user(int(user_id))
#         return Render.common_response(err_code, message, data), 200

#     def do_get_user(self, user_id):
#         data = {
#             'user_id': -1,
#             'username': '',
#             'session_id': ''
#         }
#         user = None
#         try:
#             user = UserModel.query.filter_by(id=user_id).first()
#             if not user:
#                 return 1, '用户不存在', None
#         except Exception as e:
#             return 9, e.message, None
#         return 0, '成功', user


@api.route('/<user_id>/profile')
@api.param('user_id', '用户id')
class UserProfile(Resource):
    '''
    用户资料
    get: 获取
    put: 更新
    '''
    # get
    UserProfileData = api.model('UserProfileData', {
        'user_id': fields.Integer(required=True),
        'username': fields.String(),
        'email': fields.String(),
        'description': fields.String(),
        'nickname': fields.String()
    })
    UserProfileRsp = api.model('UserProfileRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.Nested(UserProfileData)
    })
    @api.doc('get_user_profile')
    @api.marshal_with(UserProfileRsp)
    def get(self, user_id):
        '''通过user_id获取用户数据'''
        err_code, message, data = self.do_get_user_profile(int(user_id))
        return Render.common_response(err_code, message, data), 200

    def do_get_user_profile(self, user_id):
        user = UserModel.find_user(user_id=user_id)
        if not user:
            return 1, '用戶不存在', None
        data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'description': user.description,
            'nickname': user.nickname
        }
        return 0, '成功', data

    # put
    UserProfilePutReq = api.model('UserProfilePutReq', {
        'session_id': fields.String(required=True),
        'description': fields.String(),
        'nickname': fields.String()
    })
    UserProfilePutRsp = api.model('UserProfilePutRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', required=True, type=str)
    parser.add_argument('description', type=str)
    parser.add_argument('nickname', type=str)

    @api.doc('update_user_profile')
    @api.doc(body=UserProfilePutReq)
    @api.marshal_with(UserProfilePutRsp)
    def put(self, user_id):
        '''通过user_id更新用户数据'''
        # get data from post
        args = self.parser.parse_args()
        err_code, message = self.do_update_user_profile(int(user_id), args)
        return Render.common_response(err_code, message), 200

    def do_update_user_profile(self, user_id, data):
        now_user = get_login_user(data.session_id)
        if not now_user:
            return 1, '请登录'
        if now_user.id != user_id and not now_user.have_permission(2):
            return 1, '没有权限'
        user = UserModel.find_user(user_id=user_id)
        if not user:
            return 2, '被修改资料用户不存在'
        # update user by data
        if data.description:
            user.description = data.description  # TODO: 防止攻击
        if data.nickname:
            user.nickname = data.nickname  # TODO: 防止攻击
        try:
            user.save()
            return 0, '成功'
        except Exception as e:
            print(e)
            return 3, '保存用户信息失败'
