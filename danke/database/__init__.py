import click

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

db = SQLAlchemy()

'''
所有需要commit的操作应该由database目录下的函数完成
视图函数应该只调用而不手动commit
'''

def excute_sql(sql):
    # 只支持一次执行一条sql语句
    db.engine.execute(sql)


def init_db():
    from .user import User
    from .session import Session
    db.drop_all()
    db.create_all()


@click.command('reset_db')
@with_appcontext
def reset_db_command():
    '''清除已有数据，重建数据库'''
    init_db()
    with current_app.open_resource('database/admin.sql') as f:
        _data_sql = map(lambda item: item.strip(),
                        f.read().decode('utf8').split('\n'))
        for line in _data_sql:
            if line:
                excute_sql(line)
    click.echo('数据已重置')

def add_command(app):
    app.cli.add_command(reset_db_command)