import unittest
from unittest.mock import patch, mock_open
from services.google_transcription_service import convert_mp3_to_wav

class TestFileConversion(unittest.TestCase):

    @patch('os.path.isfile', return_value=True)
    @patch('ffmpeg.input')
    def test_convert_mp3_to_wav_success(self, mock_ffmpeg_input, mock_isfile):
        mock_ffmpeg_input.return_value.output.return_value.run.return_value = True
        wav_file = convert_mp3_to_wav("./test.mp3")
        self.assertEqual(wav_file, "./test.wav")
        mock_ffmpeg_input.assert_called_with("./test.mp3")

    @patch('os.path.isfile', return_value=False)
    def test_convert_mp3_to_wav_file_not_found(self, mock_isfile):
        with self.assertRaises(FileNotFoundError):
            convert_mp3_to_wav("non_existent.mp3")
