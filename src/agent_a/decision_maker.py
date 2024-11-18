import threading
import time

class DecisionMaker:
    def __init__(self):
        self.tasks = []
        self.running = False

    def add_task(self, task):
        self.tasks.append(task)

    def execute_tasks(self):
        self.running = True
        while self.running and self.tasks:
            task = self.tasks.pop(0)
            self._execute_task(task)

    def _execute_task(self, task):
        try:
            task()
        except Exception as e:
            print(f"Error executing task: {e}")

    def stop(self):
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.execute_tasks).start()
