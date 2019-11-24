import pytest
from flask import g, session
from danke.database import db


def test_register(client, app):
    rsp = client.post(
        'api/v1/auth/register', data={'username': 'dead', 'password': '123456', 'description': 'new user', 'nickname': 'dead'}
    )
    rsp_json = rsp.json
    print(rsp_json)

    # with app.app_context():
    #     assert get_db().execute(
    #         "select * from user where username = 'a'",
    #     ).fetchone() is not None


# @pytest.mark.parametrize(('username', 'password', 'message'), (
#     ('', '', b'Username is required.'),
#     ('a', '', b'Password is required.'),
#     ('test', 'test', b'already registered'),
# ))
# def test_register_validate_input(client, username, password, message):
#     response = client.post(
#         '/auth/register',
#         data={'username': username, 'password': password}
#     )
#     assert message in response.data
