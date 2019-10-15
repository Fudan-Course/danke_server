from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def reset_database():
    from .user import User
    from .session import Session
    db.drop_all()
    db.create_all()
