import os
import tempfile

import pytest
from danke import create_app
from danke.database import init_db, excute_sql

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = map(lambda item: item.strip(),
                    f.read().decode('utf8').split('\n'))


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///sqlite_test.db',
    })

    with app.app_context():
        init_db()
        for line in _data_sql:
            if line:
                excute_sql(line)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='alice', password='111111'):
        return self._client.post(
            'api/v1/auth/login',
            data={'username': username, 'password': password}
        )

    # def logout(self):
    #     return self._client.get('api/v1/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
