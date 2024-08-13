import tkinter as tk
import threading
import time

from datetime import datetime

import time

from Reminder_Handler import Reminder_Handler
from Notes_Handler import Notes_Handler
from UI import NoteifyUI

def background_task():
    while True:
        print("Running...")
        reminder_handler.check_reminders()
        time.sleep(10)

def start_app():
    # Create a daemon thread
    return True
    

reminder_handler = Reminder_Handler("Data/Reminders.json")
notes_handler = Notes_Handler("Data/notes.db")

reminder_handler.load_reminders() 

background_thread = threading.Thread(target=background_task, daemon=True)
background_thread.start()
root = tk.Tk()
app = NoteifyUI(root, reminder_handler, notes_handler)
root.mainloop()

reminder_handler.save_reminders()

while True:
    print("TEST!")
    time.sleep(1)