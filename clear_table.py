# clear_table.py
from app import db, app, FirstApp
with app.app_context():
    FirstApp.query.delete()
    db.session.commit()
print("Cleared FirstApp table.")
