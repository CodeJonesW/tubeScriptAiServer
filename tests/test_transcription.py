import unittest
from unittest.mock import patch, MagicMock, mock_open
import asyncio
from services.google_transcription_service import transcribe_audio_chunk, transcribe_audio_google

class TestAsyncTranscription(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=b'audio_content')
    @patch('google.cloud.speech.SpeechClient')
    @patch('asyncio.get_event_loop')
    def test_transcribe_audio_chunk_success(self, mock_event_loop, mock_speech_client, mock_open_file):
        # Mock the response from Google Cloud Speech-to-Text
        mock_response = MagicMock()
        mock_response.results = [
            MagicMock(alternatives=[MagicMock(transcript='Test transcript')])
        ]

        # Mock the recognize method to return the mock response
        mock_speech_client.return_value.recognize.return_value = mock_response

        # Simulate the `run_in_executor` function to return the mock_response synchronously
        async def mock_run_in_executor(executor, func, *args):
            return func(*args)
        
        # Set the return value of `run_in_executor` to call the function directly
        mock_event_loop.return_value.run_in_executor.side_effect = mock_run_in_executor

        # Call the async function under test
        transcript = asyncio.run(transcribe_audio_chunk('file_chunk.wav'))

        # Assert that the transcript is as expected
        self.assertEqual(transcript, "Test transcript\n")

        mock_speech_client.assert_called_once_with()

        # Ensure that the run_in_executor was called once with correct parameters
        mock_event_loop.return_value.run_in_executor.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data=b'audio_content')
    @patch('google.cloud.speech.SpeechClient')
    @patch('asyncio.get_event_loop')
    def test_transcribe_audio_chunk_failure(self, mock_event_loop, mock_speech_client, mock_open_file):
        # Simulate an exception being raised by the Google Cloud Speech API
        mock_speech_client.return_value.recognize.side_effect = Exception('API error')

        # Mock run_in_executor to raise an exception
        mock_event_loop.return_value.run_in_executor.side_effect = Exception('API error')

        # Test if the transcribe_audio_chunk raises an exception when the API fails
        with self.assertRaises(Exception):
            asyncio.run(transcribe_audio_chunk('file_chunk.wav'))

        # Ensure that the client was called, but an error occurred
        mock_speech_client.assert_called_once()

    @patch('services.google_transcription_service.convert_mp3_to_wav', return_value='test.wav')
    @patch('services.google_transcription_service.split_audio_into_chunks', return_value=['chunk1.wav', 'chunk2.wav'])
    @patch('services.google_transcription_service.transcribe_audio_chunk')
    def test_transcribe_audio_google_success(self, mock_transcribe_chunk, mock_split_audio, mock_convert_mp3):
        # Mock transcribe_audio_chunk to return a test transcript for each chunk
        mock_transcribe_chunk.side_effect = ['Transcript 1\n', 'Transcript 2\n']

        # Call the async function under test
        transcript, chunks = asyncio.run(transcribe_audio_google('file.mp3'))

        # Assert that the transcript is combined correctly
        self.assertEqual(transcript, 'Transcript 1\nTranscript 2\n')

        # Ensure that the correct chunks are returned
        self.assertEqual(chunks, ['chunk1.wav', 'chunk2.wav'])

        # Ensure that the conversion and splitting functions were called once
        mock_convert_mp3.assert_called_once_with('file.mp3')
        mock_split_audio.assert_called_once_with('test.wav', 30)

        # Ensure that transcribe_audio_chunk was called for each chunk
        self.assertEqual(mock_transcribe_chunk.call_count, 2)

    @patch('services.google_transcription_service.convert_mp3_to_wav', return_value='test.wav')
    @patch('services.google_transcription_service.split_audio_into_chunks', return_value=['chunk1.wav', 'chunk2.wav'])
    @patch('services.google_transcription_service.transcribe_audio_chunk')
    def test_transcribe_audio_google_failure(self, mock_transcribe_chunk, mock_split_audio, mock_convert_mp3):
        # Simulate an exception being raised during one of the chunk transcriptions
        mock_transcribe_chunk.side_effect = Exception('Chunk transcription error')

        # Test if the transcribe_audio_google raises an exception when a chunk fails
        with self.assertRaises(Exception):
            asyncio.run(transcribe_audio_google('file.mp3'))

        # Ensure that the conversion and splitting functions were called once
        mock_convert_mp3.assert_called_once_with('file.mp3')
        mock_split_audio.assert_called_once_with('test.wav', 30)

if __name__ == '__main__':
    unittest.main()
