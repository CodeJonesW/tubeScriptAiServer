import unittest
from unittest.mock import patch, MagicMock
from app import app 

class TestApiRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test client for Flask."""
        self.app = app.test_client()
        self.app.testing = True

    @patch('tasks.download_and_process.apply_async')
    def test_process_video_success(self, mock_apply_async):
        """Test /process route with valid data."""
        mock_task = MagicMock()
        mock_task.id = "test_task_id"
        mock_apply_async.return_value = mock_task

        # Simulate POST request to /process
        response = self.app.post('/process', json={
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'prompt': 'Summarize the video'
        })

        # Assert response code and JSON content
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json, {'task_id': 'test_task_id'})

        # Ensure the task is called with correct arguments
        mock_apply_async.assert_called_once_with(args=['https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'Summarize the video'])

    def test_process_video_missing_data(self):
        """Test /process route with missing data."""
        # Simulate POST request with missing URL
        response = self.app.post('/process', json={'prompt': 'Summarize the video'})

        # Assert response code and error message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'YouTube URL and prompt are required'})

    @patch('tasks.download_and_process.AsyncResult')
    def test_task_status_success(self, mock_async_result):
        """Test /status/<task_id> route with a valid task ID."""
        mock_task = MagicMock()
        mock_task.state = 'SUCCESS'
        mock_task.info = {'result': 'Transcription complete', 'status': 'Completed'}
        mock_async_result.return_value = mock_task

        # Simulate GET request to /status/test_task_id
        response = self.app.get('/status/test_task_id')

        # Assert response code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'state': 'SUCCESS',
            'result': 'Transcription complete',
            'status': 'Completed'
        })

        # Ensure the task was checked with the correct task ID
        mock_async_result.assert_called_once_with('test_task_id')

    @patch('tasks.download_and_process.AsyncResult')
    def test_task_status_pending(self, mock_async_result):
        """Test /status/<task_id> route with a task that is pending."""
        mock_task = MagicMock()
        mock_task.state = 'PENDING'
        mock_task.info = None
        mock_async_result.return_value = mock_task

        # Simulate GET request to /status/test_task_id
        response = self.app.get('/status/test_task_id')

        # Assert response code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'state': 'PENDING',
            'status': 'Pending...'
        })

    @patch('tasks.download_and_process.AsyncResult')
    def test_task_status_failure(self, mock_async_result):
        """Test /status/<task_id> route with a failed task."""
        mock_task = MagicMock()
        mock_task.state = 'FAILURE'
        mock_task.info = Exception('Task failed')
        mock_async_result.return_value = mock_task

        # Simulate GET request to /status/test_task_id
        response = self.app.get('/status/test_task_id')

        # Assert response code and content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'state': 'FAILURE',
            'status': 'Task failed'
        })

if __name__ == '__main__':
    unittest.main()
