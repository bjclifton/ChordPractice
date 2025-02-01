import pyaudio
import numpy as np
import aubio
from queue import Queue

class AudioProcessor:
    def __init__(self, queue):
        self.queue = queue
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.FRAMES_PER_BUFFER = 1024

        self.p = pyaudio.PyAudio()
        self.stream = None

        # Initialize aubio for pitch detection
        self.pitch_o = aubio.pitch("default", self.FRAMES_PER_BUFFER * 4, self.FRAMES_PER_BUFFER, self.RATE)
        self.pitch_o.set_unit("Hz")
        self.pitch_o.set_silence(-40)

    def frequency_to_note(self, freq):
        C4 = 261.63
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if freq == 0:
            return None
        semitones = 12 * np.log2(freq / C4)
        note_index = int(round(semitones)) % 12
        return note_names[note_index]

    def start_stream(self):
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.FRAMES_PER_BUFFER)
        self.listen()

    def listen(self):
        while True:
            data = self.stream.read(self.FRAMES_PER_BUFFER, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            pitch = self.pitch_o(samples)[0]

            if pitch > 0:
                note = self.frequency_to_note(pitch)
                if note:
                    self.queue.put(note)  # Send the detected note to the GUI