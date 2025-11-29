from app import app, db
from models.models import User
from sqlalchemy.exc import IntegrityError

with app.app_context():
    db.create_all()

    try:
        admin = User.query.filter_by(username='admin@example.com').first()
        if not admin:
            admin = User(
                username='admin@example.com',
                full_name='Administrator',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
    except IntegrityError:
        db.session.rollback()
        print("Integrity error. Admin already exists.")
