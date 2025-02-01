import threading
from queue import Queue
import tkinter as tk
from audio_processing import AudioProcessor
from gui import NoteDisplay

def main():
    note_queue = Queue()

    # Start the audio processing in a separate thread
    audio_processor = AudioProcessor(note_queue)
    audio_thread = threading.Thread(target=audio_processor.start_stream, daemon=True)
    audio_thread.start()

    # Start the GUI
    root = tk.Tk()
    app = NoteDisplay(root, note_queue)
    root.mainloop()

if __name__ == "__main__":
    main()
