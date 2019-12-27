from danke.database import db
from .session import Session

import time


class UserPermission(db.Model):
    '''
    1 administator
    2 user manager
    '''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    permission_type = db.Column(db.Integer)

    def __init__(self, user_id, permission_type):
        self.user_id = user_id
        self.permission_type = permission_type

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, index=True)  # 用户名
    email = db.Column(db.String(120), unique=True)  # 邮箱
    password = db.Column(db.String(120))  # 密码
    description = db.Column(db.String(240))  # 个人介绍
    avatar = db.Column(db.String(240))  # 头像链接
    nickname = db.Column(db.String(40))  # 昵称
    code = db.Column(db.String(40))  # 验证码，如果验证成功，这一项则为空串
    user_time = db.Column(db.Integer)

    def __init__(self, name, email, password, code):
        self.name = name
        self.email = email
        self.password = password
        self.description = ''
        self.nickname = name
        self.code = code
        self.avatar = ''
        self.user_time = int(time.time())

    def __repr__(self):
        return "<User:%r password:%r email:%r>" % (self.name, self.password, self.email)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def verify_code(self, code):  # 认证成功返回True
        if not self.code:
            return True  # 已认证
        if code != self.code:
            return False
        self.code = ''
        try:
            self.save()
        except:
            return False
        return True

    def have_permission(self, permission_type):
        if self.code:
            return False
        for permission in UserPermission.query.filter_by(user_id=self.id).all():
            if permission.permission_type == permission_type or permission.permisson_type == 1:
                return True
        return False

    def give_permission(self, permission_type):
        if self.code:
            return False
        try:
            for permission in UserPermission.query.filter_by(user_id=self.id).all():
                if permission.permission_type == permission_type:
                    return True
            new_permission = UserPermission(
                user_id=self.id, permission_type=permission_type)
            new_permission.save()
        except:
            return False
        return True

    def remove_permission(self, permission_type):
        try:
            for permission in UserPermission.query.filter_by(user_id=self.id).all():
                if permission.permission_type == permission_type:
                    permission.delete()
        except:
            return False
        return True

    @staticmethod
    def get_cur_user(session_id=None):
        session = Session.find_session(session_id)
        if session and session.is_valid():
            return session.user
        return None

    @staticmethod
    def find(nickname=None, user_id=None):
        if user_id:
            return User.query.filter_by(id=user_id).first()
        if nickname:
            return User.query.filter_by(nickname=nickname).first()
        return None
