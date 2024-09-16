import unittest
from unittest.mock import patch, call, MagicMock
from tasks import task_success_handler, task_failure_handler

class TestTaskHandler(unittest.TestCase):

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('tasks.delete_gcs_file') 
    @patch('os.getenv', return_value='your_gcp_bucket')
    def test_task_success_handler(self, mock_getenv, mock_delete_gcs, mock_os_path_exists, mock_os_remove):
        # Mock the result object
        result = {
            'result': {
                'file_path': './test_audio/test.mp3',
                'audio_chunks': ['./test_audio/chunk1.wav', './test_audio/chunk2.wav']
            }
        }

        # Mock the sender object
        mock_sender = MagicMock()
        mock_sender.name = 'download_and_process'

        # Call the task_success_handler with the mocked sender and result
        task_success_handler(sender=mock_sender, result=result)

        # Ensure that local files are deleted
        mock_os_remove.assert_has_calls([
            call('./test_audio/test.mp3'),
            call('./test_audio/test.wav'),
            call('./test_audio/chunk1.wav'),
            call('./test_audio/chunk2.wav')
        ], any_order=True)

        # Ensure that GCS files are deleted
        # mock_delete_gcs.assert_has_calls([
        #     call('your_gcp_bucket', 'chunk1.wav'),
        #     call('your_gcp_bucket', 'chunk2.wav')
        # ])
    
    @patch('os.remove')
    @patch('os.path.exists', return_value=True)  # Mock os.path.exists to always return True
    @patch('tasks.delete_gcs_file')  # Patch where it's used in the tasks module
    @patch('os.getenv', return_value='your_gcp_bucket')  # Mock os.getenv to return the correct bucket name
    def test_task_failure_handler(self, mock_getenv, mock_delete_gcs, mock_os_path_exists, mock_os_remove):
        # Mock the sender and exception
        mock_sender = MagicMock()
        mock_sender.name = 'download_and_process'
        exception = Exception('Task failed due to some error')

        # Mock the kwargs to simulate the failed task with file paths
        kwargs = {
            'file_path': 'test.mp3',
            'audio_chunks': ['chunk1.wav', 'chunk2.wav']
        }

        # Call the task_failure_handler with the mocked sender, kwargs, and exception
        task_failure_handler(sender=mock_sender, task_id='1234', exception=exception, kwargs=kwargs)

        # Ensure that local files are deleted
        mock_os_remove.assert_has_calls([
            call('test.mp3'),
            call('test.wav'),
            call('chunk1.wav'),
            call('chunk2.wav')
        ], any_order=True)

        # Ensure that GCS files are deleted
        # mock_delete_gcs.assert_has_calls([
        #     call('your_gcp_bucket', 'chunk1.wav'),
        #     call('your_gcp_bucket', 'chunk2.wav')
        # ])



if __name__ == '__main__':
    unittest.main()
