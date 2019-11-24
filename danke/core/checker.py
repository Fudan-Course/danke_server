import re


class Checker:
    @staticmethod
    def is_valid_username(username):
        '''判断用户名是否合法'''
        if not username:
            return False
        if not 3 <= len(username) <= 16:
            return False
        pattern = re.compile('[A-Za-z0-9_]')
        if not pattern.match(username):
            return False
        return True

    @staticmethod
    def is_valid_email(email):
        '''判断邮箱是否合法'''
        if not email:
            return False
        if not 3 <= len(email) <= 30:
            return False
        pattern = re.compile(r'^[a-zA-Z0-9\._-]+@fudan\.edu\.cn$')
        if not pattern.match(email):
            return False
        return True

    @staticmethod
    def is_valid_password(password):
        '''判断密码是否合法'''
        if not password:
            return False
        # TODO 需要检查密码是否为空串的md5！！！
        return True
