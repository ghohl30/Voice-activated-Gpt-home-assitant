import openai
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import numpy as np
import sounddevice as sd
import os
import subprocess
import io

def transcribe_speech(audio_file_path):
    audio_file= open(audio_file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

def synthesize_audio_local(text, lang='de', volume_decrease_dB=40, device=2, target_sample_rate=44100):
    # Synthesize audio using gTTS
    tts = gTTS(text=text, lang=lang)
    mp3_bytes = io.BytesIO()
    tts.write_to_fp(mp3_bytes)
    mp3_bytes.seek(0)

    # Load audio using Pydub and convert to desired format
    audio = AudioSegment.from_file(mp3_bytes, format='mp3')
    audio = audio.set_frame_rate(target_sample_rate).set_channels(device).set_sample_width(2)
    audio = audio - volume_decrease_dB  # decrease volume by specified amount

    # Save audio to file
    audio.export('synthesize.wav', format='wav')

    # Play audio using aplay
    subprocess.run(['aplay', '-D', 'hw:1,0', '-B', '8192', 'synthesize.wav'], check=True)


    # Delete temporary audio files
    # os.remove('synthesize.wav')


if __name__ == "__main__":
    synthesize_audio_local("Hey, wie geht es dir?")