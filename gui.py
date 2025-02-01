import tkinter as tk
import random
from queue import Empty

class NoteDisplay:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Guitar Chord Trainer")
        self.root.geometry("400x300")

        self.current_note = ""
        self.target_note = self.get_random_note()
        self.success_counter = 0
        self.correct_duration = 0
        self.required_duration = 30  # Number of frames to hold the correct note (~3 seconds)

        self.label = tk.Label(root, text=f"Play: {self.target_note}", font=("Helvetica", 48))
        self.label.pack(pady=50)

        self.counter_label = tk.Label(root, text=f"Score: {self.success_counter}", font=("Helvetica", 16))
        self.counter_label.place(x=300, y=10)

        self.update_display()

    def get_random_note(self):
        return random.choice(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])

    def update_display(self):
        try:
            detected_note = self.queue.get_nowait()
            if detected_note == self.target_note:
                self.correct_duration += 1
                self.label.config(bg='green')
                if self.correct_duration >= self.required_duration:
                    self.success_counter += 1
                    self.counter_label.config(text=f"Score: {self.success_counter}")
                    self.target_note = self.get_random_note()
                    self.label.config(text=f"Play: {self.target_note}", bg='white')
                    self.correct_duration = 0
            else:
                self.correct_duration = 0
                self.label.config(bg='white')
        except Empty:
            pass

        self.root.after(10, self.update_display)  # Update every 10ms