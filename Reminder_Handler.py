import os
import json
from Scheduler import Scheduler

class Reminder_Handler:
    def __init__(self, File_Path):
        self.reminders = []
        self.scheduler = Scheduler()
        self.file_path = File_Path

    def check_reminders(self):
        self.scheduler.run_pending()

    def create_reminder(self, reminder):
        self.reminders.append(reminder)
        recurring = reminder['recurring']
        if recurring == True:
            self.scheduler.schedule_recurring(reminder=reminder)
        else:
            self.scheduler.schedule_once(reminder=reminder)

    def save_reminders(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'w') as f:
                    json.dump(self.reminders, f, indent=4)
        except Exception as e:
            print(f"Failed to save reminders: {e}")
            

    def load_reminders(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as json_file:
                    self.reminders = json.load(json_file)
            else:
                return
            
            for reminder in self.reminders:
                recurring = reminder['recurring']
                if recurring == True:
                    self.scheduler.schedule_recurring(reminder=reminder)
                else:
                    self.scheduler.schedule_once(reminder=reminder)
        except Exception as e:
            print(f"Failed to load reminders: {e}")