from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key= os.getenv("OPENAI_API_KEY"),
)
import logging

logger = logging.getLogger(__name__)


def analyze_text(transcript, user_prompt):
    """Analyze the transcript based on the user's prompt using OpenAI GPT."""
    try:
        # Combine the user's prompt and transcript
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
        # logger.info(f"OpenAI response: {chat_completion.choices[0].message.content}")
        return chat_completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Error during transcript analysis: {str(e)}")
        raise