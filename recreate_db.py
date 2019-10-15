from danke import initialize_app, app
from danke.database import reset_database

initialize_app(app)

with app.app_context():
    reset_database()
