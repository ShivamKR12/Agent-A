import threading

class DecisionMaker:
    def __init__(self):
        self.tasks = []
        self.running = False
        self.command_handler = None

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

    def set_command_handler(self, handler):
        self.command_handler = handler

    def handle_command(self, command):
        if self.command_handler:
            self.command_handler(command)
        else:
            print(f"No command handler set for command: {command}")
