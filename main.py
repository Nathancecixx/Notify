#import tkinter as tk

import os
import sched
import threading
import time
import json
from turtle import back

from datetime import datetime

import schedule
import time

from plyer import notification

def background_task():
    while True:
        print("Running...")
        schedule.run_pending()
        time.sleep(10)



def send_notification(title, message):
    try:
        print(f"Notification object: {notification}")
        print(f"Title: {title}")
        print(f"Message: {message}")

        notification.notify(
            title=title,
            message=message
        ) # type: ignore
        
    except Exception as e:
        print(f"Notification failed: {e}")

#--------------------------------------------
# persisting reminders
#--------------------------------------------


def save_reminders(file_path):
    try:



        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                reminders = json.load(json_file)
        else:
            reminder = []

        

    except Exception as e:
        print(f"Failed to save reminders: {e}")
        

def load_reminders(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                reminders = json.load(json_file)
        else:
            return
        
        for reminder in reminders:
            recurring = reminder['recurring']
            if recurring == True:
                schedule_recuring(reminder)


    except Exception as e:
        print(f"Failed to load reminders: {e}")

def schedule_recuring(reminder):
    title = reminder['title']
    message = reminder['message']
    date = reminder['date']
    time = reminder['time']

    now = datetime.now()
    scheduled_time = datetime.strptime(time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)

    # If the scheduled time is earlier than the current time today, run it immediately
    if scheduled_time <= now:
        print(f"Running missed job immediately: {title}")
        send_notification(title, message)
        schedule.every().day.at(time).do(send_notification, title=title, message=message)
    else:
        print(f"Scheduling: {title} at {time}")
        schedule.every().day.at(time).do(send_notification, title=title, message=message)

def schedule_once(reminder):
    title = reminder['title']
    message = reminder['message']
    date = reminder['date']
    time = reminder['time']

    # Get the current date and time
    now = datetime.now()
    # Extract just the date
    current_date = now.date()
    print(f"Current Date: {current_date}")

    if current_date == date:
        schedule.every().day.at(time).do(send_notification, title=title, message=message)



def print_scheduled_jobs():
    for job in schedule.jobs:
        print(f"Job: {job.job_func.__name__}")
        print(f"Next Run: {job.next_run}")
        print(f"Interval: {job.interval} {job.unit}")
        print(f"Tags: {job.tags}")
        print("-" * 30)

def start_app():
    # root = tk.Tk()
    #root.withdraw()  # Hide the Tkinter window

    # Create a daemon thread
    load_reminders("Data/Reminders.json")
    background_thread = threading.Thread(target=background_task, daemon=True)
    background_thread.start()

    # root.mainloop()

start_app()

print_scheduled_jobs()

while True:
    time.sleep(1)