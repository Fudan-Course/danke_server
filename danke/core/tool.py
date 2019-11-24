'''
提供一些方便的函数
'''
import random

from danke.database.user import User
from danke.database.session import Session


def get_login_user(session_id):
    try:
        if not session_id:
            return None
        session = Session.query.filter_by(id=session_id).first()
        if not session:
            return None
        if not session.is_valid():  # TODO: 是否更新过期时间？
            return None
        user = session.user
        if not user:
            return None
        return user
    except Exception as e:
        print(e)
        return None


def get_random_char():  # 0-9A-Za-z
    ran = random.randint(0, 61)
    if ran < 10:
        return str(ran)
    ran -= 10
    if ran < 26:
        return chr(ran+ord('A'))
    ran -= 26
    return chr(ran+ord('a'))


def generate_random_code(len=6):
    ret = ''
    for i in range(len):
        ret += get_random_char()
    return ret
