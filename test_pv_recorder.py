import pvrecorder
import pvporcupine
import os 
import sounddevice as sd

def list_input_devices():
    devices = sd.query_devices()
    input_devices = []

    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_devices.append((idx, dev))
    return input_devices

KEYWORD_SENSITIVITIES = [0.5, 0.5, 0.5]

porcupine = pvporcupine.create(access_key=os.environ["PORCUPINE_ACCESS_KEY"], keywords=["porcupine", "grasshopper", "blueberry"], sensitivities=KEYWORD_SENSITIVITIES)

recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
recorder.start()