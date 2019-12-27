from contextlib import ContextDecorator


# def transaction(db):
#     if callable(db):
#         return Transaction(db)(db)
#     else:
#         return Transaction(db)


class Transaction(ContextDecorator):

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.session.rollback()
        else:
            self.db.session.commit()
