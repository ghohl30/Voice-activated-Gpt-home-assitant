import pyaudio
import wave
import time
import numpy as np

CHUNK = 16384

# Helper function to calculate RMS
def rms(audio_data):
    data = np.frombuffer(audio_data, dtype=np.int16)
    return np.sqrt(np.mean(np.square(data)))

def play_audio(file_path):
    # Create a new PyAudio instance
    audio = pyaudio.PyAudio()

    # Read the WAV file
    wav_file = wave.open(file_path, 'rb')

    # Set up the output stream
    output_stream = audio.open(
        format=audio.get_format_from_width(wav_file.getsampwidth()),
        channels=wav_file.getnchannels(),
        rate=wav_file.getframerate(),
        output=True,
        output_device_index=1
    )

    # Play the audio
    data = wav_file.readframes(CHUNK)

    while data:
        output_stream.write(data)
        data = wav_file.readframes(CHUNK)

    # Close the output stream and WAV file
    output_stream.stop_stream()
    output_stream.close()
    wav_file.close()

    # Terminate the PyAudio instance
    audio.terminate()


def record_audio(output_stereo_filename, record_seconds=3):
    # Configuration
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Choose the default input device (external microphone)
    # device_index = audio.get_default_input_device_info()["index"]
    device_index = 1

    # Open audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=device_index, frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")

    start_time = time.time()

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        current_time = time.time()

        # Check if the last chunk is silent
        if rms(data) < 20:
            if (current_time - start_time) > record_seconds:
                break
        else:
            start_time = current_time

    print("Finished recording")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    audio.terminate()

    # Save the recorded data as a stereo WAV file
    waveFile = wave.open(output_stereo_filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

if __name__ == "__main__":
    import pyaudio

    # audio = pyaudio.PyAudio()

    # print("Number of devices:", audio.get_device_count())
    # print("\nInput devices:")

    # for i in range(audio.get_device_count()):
    #     device_info = audio.get_device_info_by_index(i)
    #     if device_info['maxInputChannels'] > 0:
    #         print("Device ID:", i)
    #         print("Name:", device_info['name'])
    #         print("Channels:", device_info['maxInputChannels'])
    #         print("Default Sample Rate:", device_info['defaultSampleRate'])
    #         print("---------------------------")

    # audio.terminate()


    output_stereo_filename = "test.wav"
    path = record_audio(output_stereo_filename, record_seconds=5)
    play_audio("test.wav")