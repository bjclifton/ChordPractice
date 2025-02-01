import tkinter as tk
import random
from queue import Empty
import time

class NoteDisplay:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Guitar Chord Trainer")
        self.root.geometry("400x300")

        self.current_chord = ""
        self.target_chord = self.get_random_chord()
        self.success_counter = 0

        self.detection_window = 1  # 3 seconds window
        self.update_interval = 100  # Check every 100ms
        self.correct_chord_count = 0
        self.total_checks = 1
        self.required_percentage = 0.5  # 80% correct detections within the window

        self.label = tk.Label(root, text=f"Play: {self.target_chord}", font=("Helvetica", 48))
        self.label.pack(pady=50)

        self.counter_label = tk.Label(root, text=f"Score: {self.success_counter}", font=("Helvetica", 16))
        self.counter_label.place(x=300, y=10)

        self.start_time = time.time()
        self.update_display()

    def get_random_chord(self):
        chords = ['C', 'Cm', 'D', 'Dm', 'E', 'Em', 'F', 'Fm', 'G', 'Gm', 'A', 'Am', 'B', 'Bm']
        return random.choice(chords)

    def update_display(self):
        current_time = time.time()

        try:
            detected_chord = self.queue.get_nowait()
            self.total_checks += 1
            if detected_chord == self.target_chord:
                self.correct_chord_count += 1
                self.label.config(bg='green')
            else:
                self.label.config(bg='white')
        except Empty:
            pass

        # Check if the detection window has elapsed
        if current_time - self.start_time >= self.detection_window:
            if (self.correct_chord_count / self.total_checks) >= self.required_percentage:
                self.success_counter += 1
                self.counter_label.config(text=f"Score: {self.success_counter}")
                self.target_chord = self.get_random_chord()
                self.label.config(text=f"Play: {self.target_chord}", bg='white')

            # Reset for next window
            self.correct_chord_count = 0
            self.total_checks = 1
            self.start_time = current_time

        self.root.after(self.update_interval, self.update_display)
