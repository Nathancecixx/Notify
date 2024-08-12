from plyer import notification
from datetime import datetime
import schedule

class Scheduler:
    def __init__(self):
        self.jobs = []

    def schedule_recurring(self, reminder):
        title = reminder['title']
        message = reminder['message']
        time = reminder['time']

        now = datetime.now()
        scheduled_time = datetime.strptime(time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)

        # If the scheduled time is earlier than the current time today, run it immediately
        if scheduled_time <= now:
            print(f"Running missed job immediately: {title}")
            self.send_notification(title, message)
            job = schedule.every().day.at(time).do(self.send_notification, title=title, message=message)
        else:
            print(f"Scheduling recurring task: {title} at {time}")
            job = schedule.every().day.at(time).do(self.send_notification, title=title, message=message)

        self.jobs.append(job)

    def schedule_once(self, reminder):
        title = reminder['title']
        message = reminder['message']
        reminder_date = datetime.strptime(reminder['date'], "%Y-%m-%d").date()
        time_str = reminder['time']

        now = datetime.now()
        current_date = now.date()

        scheduled_time = datetime.combine(reminder_date, datetime.strptime(time_str, "%H:%M").time())

        if current_date == reminder_date:
            
            if scheduled_time > now:
                print(f"Scheduling one-time task: {title} at {time_str} on {reminder['date']}")
                job = schedule.every().day.at(time_str).do(self.send_notification, title=title, message=message)
                self.jobs.append(job)
            else:
                print(f"Missed the scheduled time for today: {title}")
                # Optionally, you can run it immediately or reschedule it for the next occurrence

        elif current_date < reminder_date:
            print(f"Scheduling one-time task for the future date: {title} at {time_str} on {reminder['date']}")
            delay = (scheduled_time - now).total_seconds()
            job = schedule.every(delay).seconds.do(self.send_notification, title=title, message=message)
            self.jobs.append(job)

        else:
            print(f"The scheduled date {reminder['date']} has already passed.")

    def send_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message
            ) # type: ignore
            
        except Exception as e:
            print(f"Notification failed: {e}")

    def run_pending(self):
        schedule.run_pending()

    def list_jobs(self):
        for job in self.jobs:
            print(f"Job: {job.job_func.__name__}")
            print(f"Next Run: {job.next_run}")
            print(f"Interval: {job.interval} {job.unit}")
            print(f"Tags: {job.tags}")
            print("-" * 30)
