import pyaudio
import numpy as np
from queue import Queue
from scipy.signal import butter, lfilter

class AudioProcessor:
    def __init__(self, queue):
        self.queue = queue
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.FRAMES_PER_BUFFER = 2048  # Larger buffer for better frequency resolution

        self.p = pyaudio.PyAudio()
        self.stream = None

    def frequency_to_note(self, freq):
        C4 = 261.63
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if freq == 0:
            return None
        semitones = 12 * np.log2(freq / C4)
        note_index = int(round(semitones)) % 12
        return note_names[note_index]

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def bandpass_filter(self, data, lowcut=80.0, highcut=1500.0, fs=44100, order=5):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def detect_chord(self, freqs):
        notes = [self.frequency_to_note(f) for f in freqs if f > 50]

        major_chords = {'C': ['C', 'E', 'G'], 'D': ['D', 'F#', 'A'], 'E': ['E', 'G#', 'B'],
                        'F': ['F', 'A', 'C'], 'G': ['G', 'B', 'D'], 'A': ['A', 'C#', 'E'],
                        'B': ['B', 'D#', 'F#']}
        minor_chords = {'Cm': ['C', 'D#', 'G'], 'Dm': ['D', 'F', 'A'], 'Em': ['E', 'G', 'B'],
                        'Fm': ['F', 'G#', 'C'], 'Gm': ['G', 'A#', 'D'], 'Am': ['A', 'C', 'E'],
                        'Bm': ['B', 'D', 'F#']}

        for chord, notes_list in {**major_chords, **minor_chords}.items():
            matches = sum(1 for note in notes_list if note in notes)
            if matches >= 2:  # Consider chord detected if 2 out of 3 notes match
                return chord
        return None

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

            # Apply bandpass filter to reduce noise
            filtered_samples = self.bandpass_filter(samples)

            # Perform FFT
            fft_result = np.fft.fft(filtered_samples)
            frequencies = np.fft.fftfreq(len(fft_result), 1 / self.RATE)
            magnitude = np.abs(fft_result)

            # Get top frequencies
            peak_indices = np.argsort(magnitude)[-5:]
            peak_freqs = frequencies[peak_indices]

            # Detect chord
            chord = self.detect_chord(peak_freqs)
            if chord:
                self.queue.put(chord)