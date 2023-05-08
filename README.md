# Voice Assistant Radio Controller

A voice-controlled radio controller that listens for specific keywords and performs various actions such as starting and stopping the radio, adjusting the volume, and initiating a conversation with a chatbot.

## Features

- Listen for specific keywords to control radio playback
- Adjust radio volume with voice commands
- Interact with a chatbot using voice input and output


## Installation

1. Clone this repository:

```bash
git clone https://github.com/ghohl30/Voice-activated-Gpt-home-assitant.git
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

Also make sure to install the necessary apt packages. I was a bit sloppy at keeping track of everything, but there are some audio packages that are required. (ffmpeg, portaudio, alsa,..)

3. Set your environment variables:

```bash
export PORCUPINE_ACCESS_KEY="your_porcupine_access_key"
export OPENAI_API_KEY="your_openai_key"
```

## Usage

1. Run the main script:

```bash
python listen_trigger_porcupine.py &
```

The & makes it run in the background.

You can adjust this to change the radio: 

```python 
radio_process = subprocess.Popen(["mpv", "--audio-device=alsa/hw:CARD=sndrpihifiberry,DEV=0", "--volume=30", "http://stream.srg-ssr.ch/m/drs3/mp3_128", "--input-ipc-server=/tmp/mpvsocket", "--no-terminal"])
```

I found the ones I wanted on https://www.radio-browser.info/


2. The program will listen for the following keywords:

- "Porcupine": Start the radio
- "Terminator": Stop the radio
- "Grasshopper": Initiate a conversation with the chatbot
- "Jarvis": Increase the volume by 10
- "Alexa": Decrease the volume by 10

3. To stop the program, press Ctrl+C in the terminal.