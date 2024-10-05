import os
import asyncio
import websockets
import json
import base64
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
import logging
from typing import Optional, Dict, List
import click
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration model
class Config(BaseModel):
    openai_api_key: str = Field(default=os.getenv("OPENAI_API_KEY"))
    elevenlabs_api_key: str = Field(default=os.getenv("ELEVENLABS_API_KEY"))
    elevenlabs_voice_id: str = Field(
        default=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    )
    elevenlabs_model_id: str = Field(
        default=os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2")
    )
    openai_model: str = Field(default=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    output_dir: str = Field(default=os.getenv("OUTPUT_DIR", "output"))


# Load configuration
config = Config()

# Validate required fields
if not config.openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
if not config.elevenlabs_api_key:
    raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=config.openai_api_key)

# ElevenLabs Websocket URL
ELEVENLABS_WS_URL = f"wss://api.elevenlabs.io/v1/text-to-speech/{config.elevenlabs_voice_id}/stream-input?model_id={config.elevenlabs_model_id}"

# Audio stream configuration
SAMPLE_RATE = 44100
CHANNELS = 1


async def get_llm_response(prompt: str) -> Optional[str]:
    """Asynchronously get a response from the OpenAI language model."""
    try:
        response = await client.chat.completions.create(
            model=config.openai_model, messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in LLM request: {e}")
        return None


async def text_to_speech_stream(text: str):
    """Stream text to speech using ElevenLabs websocket API and play audio in real-time."""
    audio_buffer = BytesIO()

    async with websockets.connect(ELEVENLABS_WS_URL) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "text": " ",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                    "xi_api_key": config.elevenlabs_api_key,
                }
            )
        )

        await websocket.send(json.dumps({"text": text}))
        await websocket.send(json.dumps({"text": ""}))

        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("audio"):
                    chunk = base64.b64decode(data["audio"])
                    audio_buffer.write(chunk)
                if data.get("isFinal"):
                    break
            except websockets.exceptions.ConnectionClosed:
                break

    audio_buffer.seek(0)
    audio = AudioSegment.from_mp3(audio_buffer)

    # Convert to raw audio data
    samples = audio.get_array_of_samples()
    audio_array = (
        np.array(samples).astype(np.float32) / 32768.0
    )  # Normalize to [-1.0, 1.0]

    # Play the audio
    sd.play(audio_array, samplerate=audio.frame_rate)
    sd.wait()

    # Save the complete audio file
    os.makedirs(config.output_dir, exist_ok=True)
    audio_filename = f"{len(os.listdir(config.output_dir)) + 1}.mp3"
    audio_filepath = os.path.join(config.output_dir, audio_filename)
    with open(audio_filepath, "wb") as audio_file:
        audio_buffer.seek(0)
        audio_file.write(audio_buffer.getvalue())
    logger.info(f"Complete audio saved as '{audio_filepath}'")


async def process_prompt(prompt: str):
    """Process a single prompt through the LLM and text-to-speech pipeline."""
    llm_response = await get_llm_response(prompt)
    if llm_response:
        logger.info(f"LLM Response: {llm_response}")
        await text_to_speech_stream(llm_response)
    else:
        logger.error("Failed to get LLM response.")


@click.command()
def chat():
    """CLI chat interface for LLM to Speech conversion."""
    click.echo("Welcome to the LLM Voice Generator!")
    click.echo("Type your prompts and press Enter. Type 'quit' to exit.")

    async def chat_loop():
        while True:
            user_prompt = click.prompt("You", type=str)
            if user_prompt.lower() == "quit":
                break
            click.echo("Processing...")
            await process_prompt(user_prompt)
            click.echo("Audio generated, played, and saved in the output directory.")

    asyncio.run(chat_loop())


if __name__ == "__main__":
    chat()
