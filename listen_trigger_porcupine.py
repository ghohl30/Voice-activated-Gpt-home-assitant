import os
import pvrecorder
import pvporcupine
import subprocess

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
import json

from langchain.schema import (
    AIMessage,
)

import utils

KEYWORD_SENSITIVITIES = [0.5] * 5

def main():
    porcupine = None
    recorder = None
    radio_process = None

    try:
        porcupine = pvporcupine.create(access_key=os.environ["PORCUPINE_ACCESS_KEY"], 
                                        keywords=["porcupine", 
                                                    "terminator", 
                                                    "grasshopper", 
                                                    "jarvis", 
                                                    "alexa"],
                                        sensitivities=KEYWORD_SENSITIVITIES)

        recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
        recorder.start()

        print("Listening for 'Porcupine', 'Terminator', 'Grasshopper ,'Jarvis', and 'Alexa'...")

        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)

            if keyword_index == 0:
                print("Porcupine detected. Starting radio...")
                if radio_process is None or radio_process.poll() is not None:
                    # Start the radio if it's not already running
                    radio_process = subprocess.Popen(["mpv", "--audio-device=alsa/hw:CARD=sndrpihifiberry,DEV=0", "--volume=30", "http://stream.srg-ssr.ch/m/drs3/mp3_128", "--input-ipc-server=/tmp/mpvsocket", "--no-terminal"])

            elif keyword_index == 1:
                print("terminator detected. Stopping radio...")
                if radio_process is not None and radio_process.poll() is None:
                    # Stop the radio if it's running
                    radio_process.terminate()
                    radio_process.wait()

            elif keyword_index == 2:

                recorder.delete()

                print("Grasshopper detected. Stopping radio...")
                llm = ChatOpenAI(model_name="gpt-3.5-turbo")

                # now initialize the conversation chain
                conversation = ConversationChain(llm=llm)

                
                msgAI = AIMessage(content="Wie kann ich dir helfen?", additional_kwargs={})
                utils.synthesize_audio_local(msgAI.content)
                conversation.memory.chat_memory.messages.append(msgAI)


                while True: 
                    audio_file_path = "msg.wav"
                    utils.record_audio(1, audio_file_path)
                    transcript = utils.transcribe_speech(audio_file_path)
                    if transcript[:4] == "Stop":
                        break
                    conversation.predict(input=transcript)
                    utils.synthesize_audio_local(conversation.memory.chat_memory.messages[-1].content)


                recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
                recorder.start()

                print("Listening for 'Porcupine', 'Grasshopper' and 'blueberry'...")
            elif keyword_index == 3:

                print("jarvis detected. Changing volume.")
                if radio_process is not None and radio_process.poll() is None:
                    # Send volume change command to the running radio process
                    # Get the current volume
                    get_volume_command = 'echo \'{ "command": ["get_property", "volume"] }\' | socat - /tmp/mpvsocket'
                    result = subprocess.check_output(get_volume_command, shell=True)
                    current_volume = json.loads(result)["data"]

                    # Decrease volume by 10
                    new_volume = max(current_volume + 10, 0)  # Ensure the volume doesn't go below 0

                    # Set the new volume
                    set_volume_command = f'echo \'{{ "command": ["set_property", "volume", {new_volume}] }}\' | socat - /tmp/mpvsocket'
                    os.system(set_volume_command)
                    print(f"Changed volume to {new_volume}")

            elif keyword_index == 4:
                print("Alexa detected. Changing volume")
                if radio_process is not None and radio_process.poll() is None:
                    # Send volume change command to the running radio process
                    # Get the current volume
                    get_volume_command = 'echo \'{ "command": ["get_property", "volume"] }\' | socat - /tmp/mpvsocket'
                    result = subprocess.check_output(get_volume_command, shell=True)
                    current_volume = json.loads(result)["data"]

                    # Decrease volume by 10
                    new_volume = max(current_volume - 10, 0)  # Ensure the volume doesn't go below 0

                    # Set the new volume
                    set_volume_command = f'echo \'{{ "command": ["set_property", "volume", {new_volume}] }}\' | socat - /tmp/mpvsocket'
                    os.system(set_volume_command)
                    print(f"Changed volume to {new_volume}")

    except KeyboardInterrupt:
        print("Stopped listening.")

    except Exception as e:
        if radio_process is not None and radio_process.poll() is None:
                    # Stop the radio if it's running
                    radio_process.terminate()
                    radio_process.wait()
        raise
    finally:
        if recorder is not None:
            recorder.delete()

        if porcupine is not None:
            porcupine.delete()

if __name__ == '__main__':
    main()


