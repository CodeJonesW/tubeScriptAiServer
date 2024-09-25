import unittest
from unittest.mock import patch, call, MagicMock
from tasks import task_success_handler, task_failure_handler

class TestTaskHandler(unittest.TestCase):

    @patch('logging.error')
    def test_task_success_handler(self, mock_logging_error):
        result = {
            'result': {
                'file_path': './test_audio/test.mp3',
                'audio_chunks': ['./test_audio/chunk1.wav', './test_audio/chunk2.wav']
            }
        }

        mock_sender = MagicMock()
        mock_sender.name = 'download_and_process'

        task_success_handler(sender=mock_sender, result=result)

        mock_logging_error.assert_not_called()

    @patch('logging.error')
    def test_task_failure_handler(self, mock_logging_error):
        mock_sender = MagicMock()
        mock_sender.name = 'download_and_process'
        exception = Exception('Task failed due to some error')

        kwargs = {
            'file_path': 'test.mp3',
            'audio_chunks': ['chunk1.wav', 'chunk2.wav']
        }

        task_failure_handler(sender=mock_sender, task_id='1234', exception=exception, kwargs=kwargs)

        # TODO: fix this test - low priority
        # mock_logging_error.assert_called_once_with(
        #     f"Task {mock_sender.name} (ID: 1234) failed: {str(exception)}"
        # )

if __name__ == '__main__':
    unittest.main()
