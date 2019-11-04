from flask_restplus import Namespace, Resource, fields, reqparse
from danke import settings
from danke.core.checker import Checker
from danke.core.render import Render

from danke.database.user import User
from danke.database.session import Session


api = Namespace('auth', description='用户注册、认证、登录与登出')


@api.route('/register')
class Register(Resource):
    RegisterReq = api.model('RegisterReq', {
        'username': fields.String(required=True, description='new account username', example='TianxiangZhang'),
        'email': fields.String(required=True, description='new account email', example='ztx97@qq.com'),
        'password': fields.String(required=True, description='new account password', example='123456789')
    })
    RegisterRsp = api.model('RegisterRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(required=True)
    })

    # 看似重复，实际用处不同，前者用于document，后者真正用于解析，也可以自己直接用json解析body
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True,
                        type=str, help='new account username')
    parser.add_argument('email', required=True,
                        type=str, help='new account email')
    parser.add_argument('password', required=True,
                        type=str, help='new account password')

    # 所有api应该分为三部分：handler，logic和render
    def do_register(self, username, email, password):
        if not Checker.is_valid_username(username):
            return 1, '用户名不合法'
        if not Checker.is_valid_password(password):
            return 2, '密码不合法'
        if not Checker.is_valid_email(email):
            return 3, '邮箱不合法'
        if User.query.filter_by(username=username).first():
            return 4, '用户名已被注册'
        if User.query.filter_by(email=email).first():
            return 5, '邮箱已被注册'
        try:
            user = User(username=username, email=email, password=password)
            user.save()
        except Exception as e:
            return 9, e.message
        return 0, '成功'

    @api.doc('register')
    # doc的model=XXX可以在文档中规定返回，但是不能限制真正返回结果，所以用marshal
    @api.doc(body=RegisterReq)
    @api.marshal_with(RegisterRsp)  # 通过marshal，可以自动将其中对应的项返回，未规定的项不返回
    def post(self):
        '''注册新用户'''
        args = self.parser.parse_args()
        err_code, message = self.do_register(
            args.username, args.email, args.password)
        return Render.common_response(err_code, message), 200


@api.route('/login')
class Login(Resource):
    LoginReq = api.model('LoginReq', {
        'username_or_email': fields.String(description='username or email', example='ztx97@qq.com'),
        'password': fields.String(required=True, description='new account password', example='123456789')
    })
    LoginData = api.model('LoginData', {
        'user_id': fields.Integer(required=True),
        'username': fields.String(),
        'session_id': fields.String(required=True)
    })
    LoginRsp = api.model('LoginRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.Nested(LoginData)
    })

    parser = reqparse.RequestParser()
    parser.add_argument('username_or_email', type=str,
                        help='username or email')
    parser.add_argument('password', required=True,
                        type=str, help='new user password')

    def do_login(self, username_or_email, password):
        data = {
            'user_id': -1,
            'username': '',
            'session_id': ''
        }
        if not username_or_email:
            return 1, '需要用户名或邮箱', data
        user = None
        if '@' in username_or_email:  # 邮箱
            user = User.query.filter_by(email=username_or_email).first()
            if not user:
                return 2, '邮箱不存在', data
        else:
            user = User.query.filter_by(username=username_or_email).first()
            if not user:
                return 3, '用户名不存在', data
        if user.password != password:
            return 4, '密码错误', data
        try:
            session = Session(user)
            session.save()
            data['user_id'] = user.id
            data['username'] = user.username
            data['session_id'] = session.id
        except Exception as e:
            return 9, str(e), data
        return 0, '成功', data

    @api.doc('login')
    @api.doc(body=LoginReq)
    @api.marshal_with(LoginRsp)
    def post(self):
        '''用户登录'''
        args = self.parser.parse_args()
        err_code, message, data = self.do_login(
            args.username_or_email, args.password)
        return Render.common_response(err_code, message, data), 200


# @api.route('/<code>')
# @api.param('code', 'The verify code')
# class Auth(Resource):  # 需要登陆
#     @api.doc('do_auth')
#     def get(self, code):
#         '''Auth user by code'''
#         if not NOW_USER:
#             return {'errCode': 1, 'message': 'please login'}, 200
#         if NOW_USER['authed']:
#             return {'errCode': 2, 'message': 'already authed'}, 200
#         if code == '666':
#             NOW_USER['authed'] = True
#             return {'errCode': 0, 'message': 'OK'}, 200
#         else:
#             return {'errCode': 3, 'message': '验证码错误或已过期'}, 200


# @api.route('/now_user')
# class NowUser(Resource):
#     def get(self):
#         return {'user': NOW_USER}, 200


# @api.route('/now_users')
# class NowUsers(Resource):
#     def get(self):
#         return {'users': USERS}, 200
