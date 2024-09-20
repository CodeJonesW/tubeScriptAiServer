from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.get_env_variables import load_secrets

load_dotenv()

secrets = load_secrets()

client = OpenAI(
    api_key= secrets['OPEN_AI_API_KEY'],
)
import logging

logger = logging.getLogger(__name__)


def analyze_text(transcript, user_prompt):
    logger.info('Begin ----- analyze_text')
    """Analyze the transcript based on the user's prompt using OpenAI GPT."""
    try:
        prompt = f"{user_prompt}\n\nTranscript:\n{transcript}"

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f'apply this command: {user_prompt}, to this text: {transcript}',
                }
            ],
            model="gpt-3.5-turbo",
            )
        return chat_completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Error during transcript analysis: {str(e)}")
        raise