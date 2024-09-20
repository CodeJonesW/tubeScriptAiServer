import unittest
from main import create_app, db, register_routes

class TestAuthRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a test client and test database specifically for auth routes."""
        app, celery = create_app()  # Create the app using the factory function
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth_test_users.db'  # Use a separate test database
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.app.config['JWT_SECRET_KEY'] = 'test-secret-key'

        register_routes(cls.app)  # Register the routes for testing

        # Initialize the test client
        cls.client = cls.app.test_client()

        # Set up the application context
        with cls.app.app_context():
            db.create_all()  # Create the test database

    @classmethod
    def tearDownClass(cls):
        """Tear down the test database."""
        with cls.app.app_context():
            db.drop_all()  # Drop all tables to clean up after tests

    def test_register_success(self):
        """Test successful user registration."""
        # Simulate POST request to /register
        response = self.client.post('/register', json={
            'username': 'newuser',
            'password': 'newpassword'
        })

        # Assert response code and success message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User registered successfully"})

    def test_register_user_exists(self):
        """Test registration with an existing user."""
        # Simulate POST request to /register with existing username
        self.client.post('/register', json={
            'username': 'existinguser',
            'password': 'existingpassword'
        })

        # Try to register the same user again
        response = self.client.post('/register', json={
            'username': 'existinguser',
            'password': 'existingpassword'
        })

        # Assert that registration fails with 400 error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "User already exists"})

    def test_register_missing_fields(self):
        """Test registration with missing fields."""
        # Simulate POST request to /register with missing password
        response = self.client.post('/register', json={
            'username': 'newuser'
        })

        # Assert response code and error message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Username and password are required"})

    def test_login_success(self):
        """Test successful user login."""
        # First register a new user
        self.client.post('/register', json={
            'username': 'loginuser',
            'password': 'loginpassword'
        })

        # Simulate POST request to /login with correct credentials
        response = self.client.post('/login', json={
            'username': 'loginuser',
            'password': 'loginpassword'
        })

        # Assert successful login with access token
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Register a user
        self.client.post('/register', json={
            'username': 'invaliduser',
            'password': 'validpassword'
        })

        # Simulate POST request to /login with wrong password
        response = self.client.post('/login', json={
            'username': 'invaliduser',
            'password': 'wrongpassword'
        })

        # Assert login fails with 401 status code
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"message": "Invalid credentials"})

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        # Simulate POST request to /login without username
        response = self.client.post('/login', json={
            'password': 'passwordwithoutusername'
        })

        # Assert response code and error message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Username and password are required"})

if __name__ == '__main__':
    unittest.main()
