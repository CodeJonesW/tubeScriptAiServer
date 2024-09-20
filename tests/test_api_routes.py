import unittest
from unittest.mock import patch, MagicMock
from main import create_app, db, register_routes

class TestApiRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a test client and test database."""
        app, celery = create_app()  # Create the app using the factory function
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'  # Use a test database
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

    def setUp(self):
        # Register a test user
        register_response = self.client.post('/register', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        # Check if the registration succeeded (201) or failed (if user exists, for instance)
        self.assertIn(register_response.status_code, [201, 400])

        # If registration succeeded, login the user
        if register_response.status_code == 201:
            login_response = self.client.post('/login', json={
                'username': 'testuser',
                'password': 'testpassword'
            })
            self.access_token = login_response.get_json()['access_token']
        elif register_response.status_code == 400:
            # User might already exist, so login directly
            login_response = self.client.post('/login', json={
                'username': 'testuser',
                'password': 'testpassword'
            })
            self.access_token = login_response.get_json()['access_token']

    def tearDown(self):
        """Tear down test-specific database changes."""
        with self.app.app_context():
            db.session.remove()

    def get_headers(self):
        """Helper method to generate headers with JWT token."""
        return {'Authorization': f'Bearer {self.access_token}'}

    @patch('tasks.download_and_process.apply_async')
    def test_process_video_success(self, mock_apply_async):
        """Test /process route with valid data and authentication."""
        mock_task = MagicMock()
        mock_task.id = "test_task_id"
        mock_apply_async.return_value = mock_task

        # Simulate POST request to /process with JWT headers
        response = self.client.post('/process', json={
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'prompt': 'Summarize the video'
        }, headers=self.get_headers())

        # Assert response code and JSON content
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json, {'task_id': 'test_task_id'})

        # Ensure the task is called with correct arguments
        mock_apply_async.assert_called_once_with(args=['https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'Summarize the video', 1])  # Assuming the test user has ID 1

    def test_process_video_missing_data(self):
        """Test /process route with missing data and authentication."""
        # Simulate POST request with missing URL
        response = self.client.post('/process', json={'prompt': 'Summarize the video'}, headers=self.get_headers())

        # Assert response code and error message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'YouTube URL and prompt are required'})

    @patch('tasks.download_and_process.AsyncResult')
    def test_task_status_success(self, mock_async_result):
        """Test /status/<task_id> route with a valid task ID and authentication."""
        mock_task = MagicMock()
        mock_task.state = 'SUCCESS'
        mock_task.info = {'result': 'Transcription complete', 'status': 'Completed', 'free_minutes_left': 5}
        mock_async_result.return_value = mock_task

        # Simulate GET request to /status/test_task_id with JWT headers
        response = self.client.get('/status/test_task_id', headers=self.get_headers())

        # Assert response code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'state': 'SUCCESS',
            'result': 'Transcription complete',
            'status': 'Completed',
        })

        # Ensure the task was checked with the correct task ID
        mock_async_result.assert_called_once_with('test_task_id')

    @patch('tasks.download_and_process.AsyncResult')
    def test_task_status_pending(self, mock_async_result):
        """Test /status/<task_id> route with a task that is pending and authentication."""
        mock_task = MagicMock()
        mock_task.state = 'PENDING'
        mock_task.info = None
        mock_async_result.return_value = mock_task

        # Simulate GET request to /status/test_task_id with JWT headers
        response = self.client.get('/status/test_task_id', headers=self.get_headers())

        # Assert response code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'state': 'PENDING',
            'status': 'Pending...'
        })

    @patch('tasks.download_and_process.AsyncResult')
    def test_task_status_failure(self, mock_async_result):
        """Test /status/<task_id> route with a failed task and authentication."""
        mock_task = MagicMock()
        mock_task.state = 'FAILURE'
        mock_task.info = Exception('Task failed')
        mock_async_result.return_value = mock_task

        # Simulate GET request to /status/test_task_id with JWT headers
        response = self.client.get('/status/test_task_id', headers=self.get_headers())

        # Assert response code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'state': 'FAILURE',
            'status': 'Task failed'
        })

    def test_process_video_no_auth(self):
        """Test /process route without authentication."""
        response = self.client.post('/process', json={
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'prompt': 'Summarize the video'
        })

        # Assert response code for missing authentication
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
