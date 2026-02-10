#!/usr/bin/env python3
from app import app, db, User

with app.app_context():
    # Check if test user exists
    test_user = User.query.filter_by(email='test@example.com').first()
    
    if not test_user:
        # Create test user
        test_user = User(
            email='test@example.com',
            user_type='patient',
            is_verified=True
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        print("✅ Test user created: test@example.com / password123")
    else:
        print("✅ Test user already exists: test@example.com / password123")
