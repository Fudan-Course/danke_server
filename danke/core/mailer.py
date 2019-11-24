import threading

from flask import current_app
from flask_mail import Mail, Message

import danke.config as config

mailer = Mail()


class Mailer:
    @staticmethod
    def __send_email(app, msg):
        with app.app_context():
            print('sending')
            print(msg)
            mailer.send(msg)
            print('sent!')
            print(msg)

    @staticmethod
    def send_email_sync(title, receivers, content, sender=config.MAIL_DEFAULT_SENDER):
        app = current_app._get_current_object()
        msg = Message(title, sender=sender, recipients=receivers)
        msg.body = content
        Mailer.__send_email(app, msg)

    @staticmethod
    def send_email_async(title, receivers, content, sender=config.MAIL_DEFAULT_SENDER):
        app = current_app._get_current_object()
        msg = Message(title, sender=sender, recipients=receivers)
        msg.body = content
        thr = threading.Thread(target=Mailer.__send_email, args=[app, msg])
        thr.start()
