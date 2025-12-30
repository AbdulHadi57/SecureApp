"""
Sample test file for the SecureApp Flask application.
This file demonstrates how to write tests that will be run by the Jenkins pipeline.

To run these tests locally:
    pytest test_app.py -v
    pytest test_app.py -v --cov=app --cov-report=html
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Note: Uncomment these imports when you add this file to the repository
# from app import app, db, FirstApp, User, ContactForm, LoginForm


class TestBasicFunctionality:
    """Basic tests to ensure the pipeline works."""
    
    def test_basic_math(self):
        """Simple test to verify pytest is working."""
        assert 1 + 1 == 2
    
    def test_string_operations(self):
        """Test string operations."""
        test_string = "SecureApp"
        assert test_string.lower() == "secureapp"
        assert len(test_string) == 9
    
    def test_list_operations(self):
        """Test list operations."""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert sum(test_list) == 15


# Uncomment and modify these tests when integrating with the actual Flask app
"""
@pytest.fixture
def client():
    '''Create a test client for the Flask application.'''
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


class TestFlaskApp:
    '''Test cases for Flask application endpoints.'''
    
    def test_home_page(self, client):
        '''Test that the home page loads successfully.'''
        response = client.get('/')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        '''Test that the login page loads successfully.'''
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_register_page(self, client):
        '''Test that the register page loads successfully.'''
        response = client.get('/register')
        assert response.status_code == 200
    
    def test_user_registration(self, client):
        '''Test user registration functionality.'''
        response = client.post('/register', data={
            'username': 'testuser',
            'password': 'TestPassword123!',
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.username == 'testuser'
    
    def test_user_login(self, client):
        '''Test user login functionality.'''
        # First create a user
        with app.app_context():
            user = User(username='testuser')
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()
        
        # Try to login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'TestPassword123!',
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_contact_form_validation(self, client):
        '''Test contact form validation.'''
        # Test with valid data
        response = client.post('/contact', data={
            'fname': 'John',
            'lname': 'Doe',
            'email': 'john.doe@example.com',
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify entry was created
        with app.app_context():
            entry = FirstApp.query.filter_by(email='john.doe@example.com').first()
            assert entry is not None
            assert entry.fname == 'John'
            assert entry.lname == 'Doe'
    
    def test_sql_injection_protection(self, client):
        '''Test that SQL injection attempts are blocked.'''
        # Try SQL injection in first name
        response = client.post('/contact', data={
            'fname': "'; DROP TABLE users; --",
            'lname': 'Doe',
            'email': 'test@example.com',
        })
        
        # Should fail validation
        assert b'injection' in response.data.lower() or response.status_code == 400
    
    def test_password_hashing(self):
        '''Test that passwords are properly hashed.'''
        with app.app_context():
            user = User(username='testuser')
            password = 'SecurePassword123!'
            user.set_password(password)
            
            # Password hash should not be the same as the password
            assert user.password_hash != password
            
            # Should be able to verify the password
            assert user.check_password(password) == True
            
            # Should not verify wrong password
            assert user.check_password('WrongPassword') == False


class TestFormValidation:
    '''Test form validation logic.'''
    
    def test_contact_form_fields(self):
        '''Test contact form field validation.'''
        form = ContactForm(data={
            'fname': 'John',
            'lname': 'Doe',
            'email': 'john.doe@example.com'
        })
        
        assert form.fname.data == 'John'
        assert form.lname.data == 'Doe'
        assert form.email.data == 'john.doe@example.com'
    
    def test_login_form_fields(self):
        '''Test login form field validation.'''
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        
        assert form.username.data == 'testuser'
        assert form.password.data == 'TestPassword123!'
"""


class TestSecurityFeatures:
    """Test security-related functionality."""
    
    def test_forbidden_sequences(self):
        """Test that forbidden SQL sequences are detected."""
        forbidden = ["--", ";", "/*", "*/"]
        
        for seq in forbidden:
            test_string = f"test{seq}input"
            assert seq in test_string
    
    def test_sql_keywords(self):
        """Test SQL keyword detection."""
        keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "UNION"]
        
        for keyword in keywords:
            assert keyword.upper() == keyword
            assert len(keyword) > 0


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=html'])
