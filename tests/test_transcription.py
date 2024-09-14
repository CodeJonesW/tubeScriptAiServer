import unittest
from unittest.mock import patch, MagicMock
from services.google_transcription_service import transcribe_audio_chunk

class TestTranscription(unittest.TestCase):

    @patch('services.google_transcription_service.upload_to_gcs', return_value='gs://bucket/file.wav')
    @patch('google.cloud.speech.SpeechClient')
    def test_transcribe_audio_chunk_success(self, mock_speech_client, mock_upload_to_gcs):
        # Mock the response from Google Cloud Speech-to-Text
        mock_response = MagicMock()
        mock_response.results = [
            MagicMock(alternatives=[MagicMock(transcript='Test transcript')])
        ]

        # Set the mock client's long_running_recognize method to return the mocked response
        mock_speech_client.return_value.long_running_recognize.return_value.result.return_value = mock_response
        
        # Call the function under test
        transcript = transcribe_audio_chunk('bucket', 'file_chunk.wav')

        # Assert that the transcript is as expected
        self.assertEqual(transcript, "Test transcript\n")

        # Ensure that upload_to_gcs was called once
        mock_upload_to_gcs.assert_called_once_with('bucket', 'file_chunk.wav')

        # Ensure that the Google Cloud Speech client was called as expected
        mock_speech_client.assert_called_once()

    @patch('google.cloud.speech.SpeechClient')
    def test_transcribe_audio_chunk_failure(self, mock_speech_client):
        # Simulate an exception being raised by the Google Cloud Speech API
        mock_speech_client.return_value.long_running_recognize.side_effect = Exception('API error')

        # Test if the transcribe_audio_chunk raises an exception when the API fails
        with self.assertRaises(Exception):
            transcribe_audio_chunk('bucket', 'file_chunk.wav')

        # Ensure that the client was called, but an error occurred
        mock_speech_client.assert_called_once()

if __name__ == '__main__':
    unittest.main()
