# LLM to Speech Conversion Tool

This tool takes user prompts, generates responses using OpenAI's language models, and converts those responses to speech using ElevenLabs' text-to-speech API with real-time audio playback.

## Prerequisites

- Python 3.7+
- OpenAI API key
- ElevenLabs API key
- FFmpeg (required for audio processing)

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
   pip install openai websockets pydantic click sounddevice numpy pydub
   ```

4. Install FFmpeg:

   - On Ubuntu or Debian:
     ```
     sudo apt-get install ffmpeg
     ```
   - On macOS using Homebrew:
     ```
     brew install ffmpeg
     ```
   - On Windows using Chocolatey:
     ```
     choco install ffmpeg
     ```

5. Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

## Configuration

You can modify the following environment variables to customize the tool's behavior:

- `ELEVENLABS_VOICE_ID`: The ID of the ElevenLabs voice to use (default is "21m00Tcm4TlvDq8ikWAM")
- `ELEVENLABS_MODEL_ID`: The ID of the ElevenLabs model to use (default is "eleven_turbo_v2")
- `OPENAI_MODEL`: The OpenAI model to use (default is "gpt-3.5-turbo")
- `OUTPUT_DIR`: Directory to save audio files (default is "output")

Add these to your `.env` file if you want to override the defaults.

## Usage

1. Ensure your virtual environment is activated.

2. Run the script:

   ```
   python app/llm_speech.py
   ```

3. Enter your prompts when asked. The script will generate responses, convert them to speech, and play the audio in real-time.

4. To exit the program, type 'quit' when prompted for input.

5. Generated audio files will be saved in the `output` directory.

## Troubleshooting

If you encounter any issues, check the following:

1. Ensure your API keys are correctly set in the `.env` file.
2. Verify that you have an active internet connection.
3. Check that FFmpeg is correctly installed and accessible from the command line.
4. Make sure your system's audio output is properly configured.
5. Check the console output for any error messages.

For any other issues, please open an issue on the project's GitHub repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
