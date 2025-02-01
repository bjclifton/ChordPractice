import platform
import pyaudio
import wave

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

print("Available audio devices:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

# Select the first input device by default (can customize)
device_choice = int(input("Enter the device number you want to use: "))

try:
    stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                input=True,
                input_device_index=device_choice,
                frames_per_buffer=1024)
    
    # Record 5 seconds of audio
    print("Recording...")
    frames = []
    for i in range(0, int(44100 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)
    print("Recording complete.")
    
    stream.stop_stream()
    stream.close()
    
    # Save to file
    wf = wave.open("output.wav", "wb")
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    p.terminate()
    
except OSError as e:
    print(f"Error opening audio stream: {e}")
    print("Make sure the correct input device is selected.")



