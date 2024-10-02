import os
import asyncio
import aiohttp
import hashlib
import json
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
import logging
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration model
class Config(BaseModel):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    elevenlabs_api_key: str = Field(..., env="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field(
        default="21m00Tcm4TlvDq8ikWAM", env="ELEVENLABS_VOICE_ID"
    )
    openai_model: str = Field(default="gpt-3.5-turbo")
    output_dir: str = Field(default="output")
    cache_dir: str = Field(default="cache")


# Load configuration
config = Config()

# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=config.openai_api_key)

# ElevenLabs API URL
ELEVENLABS_API_URL = (
    f"https://api.elevenlabs.io/v1/text-to-speech/{config.elevenlabs_voice_id}"
)

# Cache for LLM responses and audio files
llm_cache: Dict[str, str] = {}
audio_cache: Dict[str, str] = {}


def get_cache_key(data: str) -> str:
    """Generate a unique cache key for a given string."""
    return hashlib.md5(data.encode()).hexdigest()


async def get_llm_response(prompt: str) -> Optional[str]:
    """Asynchronously get a response from the OpenAI language model, using cache if available."""
    cache_key = get_cache_key(prompt)
    if cache_key in llm_cache:
        logger.info("Using cached LLM response")
        return llm_cache[cache_key]

    try:
        response = await client.chat.completions.create(
            model=config.openai_model, messages=[{"role": "user", "content": prompt}]
        )
        llm_response = response.choices[0].message.content
        llm_cache[cache_key] = llm_response

        # Save cache to file
        os.makedirs(config.cache_dir, exist_ok=True)
        with open(os.path.join(config.cache_dir, "llm_cache.json"), "w") as f:
            json.dump(llm_cache, f)

        return llm_response
    except Exception as e:
        logger.error(f"Error in LLM request: {e}")
        return None


async def text_to_speech(text: str, session: aiohttp.ClientSession) -> Optional[str]:
    """Asynchronously convert text to speech using ElevenLabs API, using cache if available."""
    cache_key = get_cache_key(text)
    if cache_key in audio_cache:
        logger.info("Using cached audio file")
        return audio_cache[cache_key]

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": config.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    try:
        async with session.post(
            ELEVENLABS_API_URL, json=data, headers=headers
        ) as response:
            if response.status == 200:
                audio_content = await response.read()
                filename = f"output_{cache_key}.mp3"
                filepath = os.path.join(config.output_dir, filename)
                os.makedirs(config.output_dir, exist_ok=True)
                with open(filepath, "wb") as audio_file:
                    audio_file.write(audio_content)
                audio_cache[cache_key] = filepath

                # Save cache to file
                with open(os.path.join(config.cache_dir, "audio_cache.json"), "w") as f:
                    json.dump(audio_cache, f)

                return filepath
            else:
                logger.error(
                    f"Error in text-to-speech request: {await response.text()}"
                )
                return None
    except Exception as e:
        logger.error(f"Error in text-to-speech request: {e}")
        return None


async def process_prompt(prompt: str, session: aiohttp.ClientSession) -> None:
    """Process a single prompt through the LLM and text-to-speech pipeline."""
    llm_response = await get_llm_response(prompt)
    if llm_response:
        logger.info(f"LLM Response: {llm_response}")

        audio_filepath = await text_to_speech(llm_response, session)
        if audio_filepath:
            logger.info(f"Audio saved as '{audio_filepath}'")
        else:
            logger.error("Failed to generate audio.")
    else:
        logger.error("Failed to get LLM response.")


async def main():
    # Load caches from files
    global llm_cache, audio_cache
    os.makedirs(config.cache_dir, exist_ok=True)
    if os.path.exists(os.path.join(config.cache_dir, "llm_cache.json")):
        with open(os.path.join(config.cache_dir, "llm_cache.json"), "r") as f:
            llm_cache = json.load(f)
    if os.path.exists(os.path.join(config.cache_dir, "audio_cache.json")):
        with open(os.path.join(config.cache_dir, "audio_cache.json"), "r") as f:
            audio_cache = json.load(f)

    async with aiohttp.ClientSession() as session:
        while True:
            user_prompt = input("Enter your prompt for the LLM (or 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            await process_prompt(user_prompt, session)


if __name__ == "__main__":
    asyncio.run(main())

# TODO: Implement a proper CLI interface using Click or Typer
# This would provide a more user-friendly interface and allow for
# additional command-line options and better help documentation.

# TODO: Consider containerizing the application
# Containerization would make deployment and scaling easier, ensuring
# consistent environments across different systems.
