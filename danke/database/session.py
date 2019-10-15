import random
import time

from danke.database import db


class Session(db.Model):
    id = db.Column(db.String(120), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(
        'User', backref=db.backref('sessions', lazy='dynamic'))

    login_time = db.Column(db.Integer)
    expiration_time = db.Column(db.Integer)

    def __init__(self, user, login_time=None, valid_time=3600 * 24 * 7):
        if not login_time:
            login_time = int(time.time())
        self.id = str(random.randint(1, int(1e50)))
        self.user = user
        self.login_time = login_time
        self.expiration_time = login_time + valid_time

    def __repr__(self):
        print('<Session_id %r User_id %r>' % (self.id, self.user_id))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_valid(self, now=None):
        if not now:
            now = int(time.time())
        if now < self.expiration_time:
            return True
        else:
            self.delete()
            return False
