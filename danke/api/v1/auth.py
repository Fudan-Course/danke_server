from flask_restplus import Namespace, Resource, fields, reqparse
from flask import request

from danke.core.checker import Checker
from danke.core.render import Render
from danke.core.mailer import Mailer
from danke.core.tool import *

from danke.database.user import User
from danke.database.session import Session


api = Namespace('auth', description='用户注册、认证、登录与登出')


def send_verify_code(code, receiver):
    try:
        Mailer.send_email_sync(title='旦课邮箱验证码', receivers=[
                               receiver], content='验证码：'+code)
        return 0, '发送成功'
    except Exception as e:
        print(e)  # need a logger
        return 1, '发送失败'


@api.route('/register')
class Register(Resource):
    # post
    RegisterReq = api.model('RegisterReq', {
        'username': fields.String(required=True, description='new account username', example='TianxiangZhang'),
        'email': fields.String(required=True, description='new account email', example='16307130026@fudan.edu.cn'),
        'password': fields.String(required=True, description='new account password', example='123456789')
    })
    RegisterRsp = api.model('RegisterRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(required=True)
    })
    # model用于document，aprser用于解析body
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True,
                        type=str, help='new account username')
    parser.add_argument('email', required=True,
                        type=str, help='new account email')
    parser.add_argument('password', required=True,
                        type=str, help='new account password')

    @api.doc('register')
    @api.expect(RegisterReq, validate=False)
    @api.marshal_with(RegisterRsp)  # 通过marshal，可以自动将其中对应的项返回，未规定的项不返回
    def post(self):
        '''注册新用户'''
        print(request.data)
        print(api.payload)
        kwargs = self.parser.parse_args()
        err_code, message = self.do_register(
            kwargs.username, kwargs.email, kwargs.password)
        return Render.common_response(err_code, message), 200

    def do_register(self, username, email, password):
        if not Checker.is_valid_username(username):
            return 1, '用户名不合法'
        if not Checker.is_valid_password(password):
            return 2, '密码不合法'
        if not Checker.is_valid_email(email):
            return 3, '邮箱不合法'
        if User.query.filter_by(name=username).first():
            return 4, '用户名已被注册'
        if User.query.filter_by(email=email).first():
            return 5, '邮箱已被注册'
        try:
            user = User(name=username, email=email,
                        password=password, code=generate_random_code())
            user.save()
            res = send_verify_code(user.code, user.email)
            print(res)
        except Exception as e:
            return 9, str(e)
        return 0, '成功'


@api.route('/login')
class Login(Resource):
    # post
    LoginReq = api.model('LoginReq', {
        'username_or_email': fields.String(required=True, example='16307130026@fudan.edu.cn'),
        'password': fields.String(required=True, example='123456789')
    })
    LoginData = api.model('LoginData', {
        'user_id': fields.Integer(required=True),
        'nickname': fields.String(),
        'session_id': fields.String(required=True)
    })
    LoginRsp = api.model('LoginRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.Nested(LoginData)
    })
    parser = reqparse.RequestParser()
    parser.add_argument('username_or_email', type=str)
    parser.add_argument('password', required=True, type=str)

    @api.doc('login')
    @api.expect(LoginReq)
    @api.marshal_with(LoginRsp)
    def post(self):
        '''用户登录'''
        kwargs = self.parser.parse_args()
        err_code, message, data = self.do_login(
            kwargs.username_or_email, kwargs.password)
        return Render.common_response(err_code, message, data), 200

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
            user = User.query.filter_by(name=username_or_email).first()
            if not user:
                return 3, '用户名不存在', data
        if user.password != password:
            return 4, '密码错误', data
        try:
            session = Session(user)
            session.save()
            data['user_id'] = user.id
            data['nickname'] = user.nickname
            data['session_id'] = session.id
        except Exception as e:
            return 9, str(e), data
        return 0, '成功', data


@api.route('/logout')
class Logout(Resource):
    # pos
    LogoutReq = api.model('LogoutReq', {
        'session_id': fields.String(required=True)
    })
    LogoutRsp = api.model('LogoutRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', required=True, type=str)

    @api.doc('logout')
    @api.expect(LogoutReq)
    @api.marshal_with(LogoutRsp)
    def post(self):
        '''用户登出'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_logout(kwargs.session_id)
        return Render.common_response(err_code, message), 200

    def do_logout(self, session_id):
        session = Session.find_session(session_id)
        if session:
            session.delete()
        return 0, '登出成功'


@api.route('/verify')
class Verify(Resource):
    # post
    VerifyPostReq = api.model('VerifyPostReq', {
        'session_id': fields.String(required=True),
        'code': fields.String(required=True)
    })
    VerifyPostRsp = api.model('VerifyPostRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', type=str)
    parser.add_argument('code', required=True)

    @api.doc('verify')
    @api.expect(VerifyPostReq)
    @api.marshal_with(VerifyPostRsp)
    def post(self):
        '''用户邮箱认证'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_verify(kwargs)
        return Render.common_response(err_code, message), 200

    def do_verify(self, data):
        user = get_login_user(data.session_id)
        if not user:
            return 1, '请登录'
        if user.verify_code(data.code):
            return 0, '成功'
        else:
            return 2, '失败'


@api.route('/send_code')
class SendCode(Resource):
    '''
    POST: 发送邮箱验证码
    '''
    # post
    SendCodeReq = api.model('SendCodeReq', {
        'session_id': fields.String(required=True)
    })
    SendCodeRsp = api.model('SendCodeRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', type=str)
    @api.doc('send_verify_code')
    @api.expect(SendCodeReq)
    @api.marshal_with(SendCodeRsp)
    def post(self):
        '''发送邮箱验证码'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_send_code(kwargs)
        return Render.common_response(err_code, message), 200

    def do_send_code(self, data):
        user = get_login_user(data.session_id)
        if not user:
            return 1, '请登录'
        send_verify_code(user.code, user.email)
        return 0, '发送成功'
