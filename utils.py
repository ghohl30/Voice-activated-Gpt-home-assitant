import pyaudio
import numpy as np
import wave
import time
import openai
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import numpy as np
import sounddevice as sd
import os
import subprocess
import io


# Parameters
THRESHOLD = 35  # Adjust this value based on your environment
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024 * 8  # Larger buffer size to prevent buffer overflows
DEVICE_INDEX = 1
OUTPUT_FILE = "test.wav"
SILENCE_DURATION = 4

def is_silent(audio_data, threshold):
    rms = np.sqrt(np.mean(np.square(audio_data)))
    print(rms)
    return rms < threshold

def record_audio(device_index, output_file):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input_device_index=device_index,
                        input=True, frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []
    silence_start = None

    while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        frames.append(data)

        if is_silent(audio_data, THRESHOLD):
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start >= SILENCE_DURATION:
                break
        else:
            silence_start = None

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def convert_mono_to_stereo(input_file, output_file):
    mono_audio = AudioSegment.from_wav(input_file)
    stereo_audio = mono_audio.set_channels(2)
    stereo_audio.export(output_file, format="wav")

def play_wav(file, device_index):
    # Open the wave file
    wf = wave.open(file, 'rb')

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the stream
    stream = audio.open(
        format=audio.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
        output_device_index=device_index
    )

    # Play the audio
    print(f"Playing {file} on device {device_index}...")
    data = wf.readframes(1024)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)

    # Stop the stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    audio.terminate()

def transcribe_speech(audio_file_path):
    audio_file= open(audio_file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript['text'])
    return transcript['text']

def synthesize_audio_local(text, lang='de', volume_decrease_dB=40, device=2, target_sample_rate=44100):
    print(text)
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
    os.remove('synthesize.wav')


if __name__ == "__main__":
    record_audio(DEVICE_INDEX, OUTPUT_FILE)
    input_file = "test.wav"
    output_file = "tests.wav"
    convert_mono_to_stereo(input_file, output_file)
    play_wav(output_file, 0)
