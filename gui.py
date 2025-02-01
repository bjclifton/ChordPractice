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

        self.current_note = ""
        self.target_note = self.get_random_note()
        self.success_counter = 0

        self.detection_window = 1  # Duration of the window in seconds
        self.update_interval = 1  # Interval to check notes in ms
        self.correct_note_count = 0
        self.total_checks = 1
        self.required_percentage = 0.6  # 80% correct detections within the window

        self.label = tk.Label(root, text=f"Play: {self.target_note}", font=("Helvetica", 48))
        self.label.pack(pady=50)

        self.counter_label = tk.Label(root, text=f"Score: {self.success_counter}", font=("Helvetica", 16))
        self.counter_label.place(x=300, y=10)

        self.start_time = time.time()
        self.update_display()

    def get_random_note(self):
        return random.choice(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])

    def update_display(self):
        current_time = time.time()

        try:
            detected_note = self.queue.get_nowait()
            self.total_checks += 1
            if detected_note == self.target_note:
                self.correct_note_count += 1
                self.label.config(bg='green')
            else:
                self.label.config(bg='white')
        except Empty:
            pass

        # Check if the detection window has elapsed
        if current_time - self.start_time >= self.detection_window:
            if (self.correct_note_count / self.total_checks) >= self.required_percentage:
                self.success_counter += 1
                self.counter_label.config(text=f"Score: {self.success_counter}")
                self.target_note = self.get_random_note()
                self.label.config(text=f"Play: {self.target_note}", bg='white')
            
            # Reset for the next window
            self.correct_note_count = 0
            self.total_checks = 1
            self.start_time = current_time

        self.root.after(self.update_interval, self.update_display)  
