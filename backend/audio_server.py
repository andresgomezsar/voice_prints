import os
import wave
import time
import logging
import threading
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

from flask import Flask, request, jsonify
from pyngrok import ngrok

import json
import mlx_whisper
from textblob import TextBlob
from transcription import transcribe_audio
from voice_metrics import calculate_voice_metrics

import asyncio
from vad_processor import process_vad 
import subprocess

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# audio config
CHANNELS = 1  # mono
SAMPLE_WIDTH = 2  # 16 bits
SAMPLE_RATE = 16000
COMPILE_INTERVAL = 30  # 30 seconds

AUDIO_DIR = "audio"
VOICE_DATA_DIR = "voice_data"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VOICE_DATA_DIR, exist_ok=True)

class AudioBuffer:
    def __init__(self):
        self.buffer: List[bytes] = []
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def add_data(self, data: bytes):
        with self.lock:
            self.buffer.append(data)
            self.last_update = time.time()
    
    def get_and_clear(self) -> List[bytes]:
        with self.lock:
            data = self.buffer
            self.buffer = []
            return data

# global audio buffers for different users -- not needed rn
audio_buffers: Dict[str, AudioBuffer] = defaultdict(AudioBuffer)

def save_audio(uid, filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(44100)  # 44.1kHz
        wf.writeframes(audio_buffers[uid].get_and_clear())

def compile_audio(uid: str):
    """Compile audio data for a user every COMPILE_INTERVAL seconds."""
    logger.info(f"Compiler thread started for user {uid}")
    while True:
        logger.info(f"Waiting for {COMPILE_INTERVAL} seconds before compiling audio for user {uid}")
        time.sleep(COMPILE_INTERVAL)

        buffer = audio_buffers.get(uid)
        if not buffer:
            logger.info(f"No buffer found for user {uid}")
            continue

        audio_data = buffer.get_and_clear()
        if not audio_data:
            logger.info(f"No audio data to compile for user {uid}")
            continue

        # combine all audio chunks
        combined_audio = b''.join(audio_data)
        logger.info(f"Compiling audio data for user {uid}")

        # Create WAV file
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        filename = f"{timestamp}_{uid}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Save the audio file
        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(SAMPLE_WIDTH)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(combined_audio)
            logger.info(f"Saved audio file: {filepath}")
        except Exception as e:
            logger.error(f"Error saving audio file {filepath}: {e}")
            continue  # skip to the next iteration

        # VAD processing
        try:
            # Perform VAD processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio, timestamps = loop.run_until_complete(process_vad(filepath, method='hybrid'))
            loop.close()
            logger.info(f"Performed VAD processing on audio file: {filepath}")
        except Exception as e:
            logger.error(f"Error during VAD processing for file {filepath}: {e}")
            continue  # Skip to the next iteration

        # Transcribe the audio file
        try:
            transcription = transcribe_audio(filepath)
            logger.info(f"Transcribed audio for user {uid}")
        except Exception as e:
            logger.error(f"Error transcribing audio file {filepath}: {e}")
            continue  # Skip to the next iteration

        # Calculate voice metrics
        try:
            duration_seconds = len(combined_audio) / (SAMPLE_RATE * SAMPLE_WIDTH)
            metrics = calculate_voice_metrics(transcription, duration_seconds)
            logger.info(f"Calculated voice metrics for user {uid}")
        except Exception as e:
            logger.error(f"Error calculating voice metrics for user {uid}: {e}")
            continue  # Skip to the next iteration

        # Update the JSON file with transcription and metrics
        try:
            update_json(uid, transcription, metrics)
            logger.info(f"Updated JSON file for user {uid}")
        except Exception as e:
            logger.error(f"Error updating JSON for user {uid}: {e}")

        # Delete the audio file after processing
        try:
            os.remove(filepath)
            logger.info(f"Deleted audio file: {filepath}")
        except Exception as e:
            logger.error(f"Error deleting audio file {filepath}: {e}")

def update_json(uid: str, transcription: str, metrics: dict):
    """Update JSON file with transcription and metrics."""
    data = {
        "uid": uid,
        "timestamp": datetime.now().isoformat(),
        "transcription": transcription,
        "metrics": metrics
    }

    date_str = datetime.now().strftime("%Y-%m-%d")
    json_filename = f"{date_str}.json"
    json_filepath = os.path.join(VOICE_DATA_DIR, json_filename)

    with open(json_filepath, 'a') as json_file:
        json.dump(data, json_file)
        json_file.write('\n')  # Ensure each entry is on a new line

    logger.info(f"Updated JSON file: {json_filepath}")

@app.route('/audio', methods=['POST'])
def handle_audio():
    """Handle incoming audio data."""
    try:
        uid = request.args.get('uid')
        if not uid:
            return jsonify({"error": "Missing uid parameter"}), 400

        audio_data = request.get_data()
        if not audio_data:
            return jsonify({"error": "No audio data received"}), 400

        # Initialize buffer and compiler thread for new users
        if uid not in audio_buffers:
            audio_buffers[uid] = AudioBuffer()
            start_compiler_for_user(uid)  # Ensure this line is present

        # Add data to user's buffer
        audio_buffers[uid].add_data(audio_data)
        logger.info(f"Received audio data from user {uid}, bytes_received: {len(audio_data)}")

        return jsonify({
            "message": "Audio data received successfully",
            "bytes_received": len(audio_data)
        }), 200

    except Exception as e:
        logger.error(f"Error handling audio data: {str(e)}")
        return jsonify({"error": str(e)}), 500

def start_ngrok():
    """Start ngrok tunnel to expose the local server."""
    try:
        public_url = ngrok.connect(5000).public_url
        logger.info(f"ngrok tunnel established at: {public_url}")
        return public_url
    
    except Exception as e:
        logger.error(f"Error starting ngrok: {str(e)}")
        return None

def start_compiler_for_user(uid):
    thread = threading.Thread(target=compile_audio, args=(uid,), daemon=True)
    thread.start()
    return thread

def create_venv_and_install_requirements():
    """Create a virtual environment and install required packages."""
    try:
        subprocess.run(["python3", "-m", "venv", "venv"], check=True)
        subprocess.run(["venv/bin/pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("Virtual environment created and requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating virtual environment or installing requirements: {e}")

def main():
    PORT = 8080  # fixed port 5000 is airdrop on macs

    # Create virtual environment and install requirements
    create_venv_and_install_requirements()

    # starting ngrok in a separate thread
    ngrok_url = ngrok.connect(PORT).public_url
    logger.info(f"ngrok tunnel established at: {ngrok_url}")

    # stating the Flask app
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()