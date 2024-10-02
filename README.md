# LLM to Speech Conversion Tool

This tool takes user prompts, generates responses using OpenAI's language models, and converts those responses to speech using ElevenLabs' text-to-speech API.

## Prerequisites

- Python 3.7+
- OpenAI API key
- ElevenLabs API key

## Installation

1. Clone this repository:
   ```
   git clone https://your-repository-url.git
   cd llm-to-speech-tool
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

## Usage

1. Ensure your virtual environment is activated.

2. Run the script:
   ```
   python llm_to_speech.py
   ```

3. Enter your prompts when asked. The script will generate responses and convert them to speech.

4. To exit the program, type 'quit' when prompted for input.

5. Generated audio files will be saved in the `output` directory.

## Caching

The tool caches both LLM responses and generated audio files to improve efficiency. Cached data is stored in the `cache` directory.

## Configuration

You can modify the following parameters in the `Config` class within the script:

- `elevenlabs_voice_id`: The ID of the ElevenLabs voice to use
- `openai_model`: The OpenAI model to use (default is "gpt-3.5-turbo")
- `output_dir`: Directory to save audio files (default is "output")
- `cache_dir`: Directory to store cache files (default is "cache")

## Troubleshooting

If you encounter any issues, check the following:

1. Ensure your API keys are correctly set in the `.env` file.
2. Verify that you have an active internet connection.
3. Check the console output for any error messages.

For any other issues, please open an issue on the project's GitHub repository.

