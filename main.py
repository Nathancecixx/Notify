#import tkinter as tk

import os
import sched
import threading
import time
import json
from turtle import back

from datetime import datetime

import time

from Reminder_Handler import Reminder_Handler

def background_task():
    while True:
        print("Running...")
        reminder_handler.check_reminders()
        time.sleep(10)


#--------------------------------------------
# persisting reminders
#--------------------------------------------




def start_app():
    # root = tk.Tk()
    #root.withdraw()  # Hide the Tkinter window

    # Create a daemon thread
    background_thread = threading.Thread(target=background_task, daemon=True)
    background_thread.start()

    # root.mainloop()

reminder_handler = Reminder_Handler("Data/Reminders.json")

reminder_handler.load_reminders()

reminder =   {
        "title": "WORKOUT TIME!!",
        "message": "Time to workout buddy!!",
        "date": "2024-08-10",
        "time": "10:00",
        "recurring": True
    }

#reminder_handler.create_reminder(reminder)

#start_app()

reminder_handler.save_reminders()

#while True:
#    time.sleep(1)