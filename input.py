import platform
import pyaudio
import wave
import numpy as np
import aubio

if platform.system() == 'Windows':
    print("Running on Windows")
    # Windows-specific settings
elif platform.system() == 'Darwin':  # macOS
    print("Running on macOS")  
    # macOS-specific settings
elif platform.system() == 'Linux':
    print("Running on Linux")
    # Linux-specific settings


p = pyaudio.PyAudio()
# Check the default input device
default_device_info = p.get_default_input_device_info()
device_choice = None
if default_device_info['name'] == 'None':
    print("No default input device found.")
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Device {i}: {info['name']}")
    device_choice = int(input("Enter the device number you want to use: "))
    
else:
    print(f"Using default input device: {default_device_info['name']}")
    device_choice = p.get_default_input_device_info()['index']


# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 1024

# Initialize aubio pitch detection
pitch_o = aubio.pitch("default", FRAMES_PER_BUFFER * 4, FRAMES_PER_BUFFER, RATE)
pitch_o.set_unit("Hz")
pitch_o.set_silence(-40)  # Ignore silence/noise below -40 dB

# Function to map frequency to note
def frequency_to_note(freq):
    C4 = 261.63  # Frequency of middle C
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if freq == 0:
        return None
    
    # Calculate number of semitones from C4
    semitones = 12 * np.log2(freq / C4)
    
    # Adjust for nearest note
    note_index = int(round(semitones)) % 12
    
    return note_names[note_index]


try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_choice,
                    frames_per_buffer=FRAMES_PER_BUFFER)
    print("Listening... Play your chords!")

    while True:
        # Read audio chunk from the stream
        data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)

        # Detect pitch using aubio
        pitch = pitch_o(samples)[0]

        # Map frequency to note
        if pitch > 0:
            note = frequency_to_note(pitch)
            if note:
                print(f"Detected note: {note} ({pitch:.2f} Hz)")

except KeyboardInterrupt:
    print("\nStopping...")
    stream.stop_stream()
    stream.close()
    p.terminate()

except OSError as e:
    print(f"Error opening audio stream: {e}")
    print("Make sure the correct input device is selected.")