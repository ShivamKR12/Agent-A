import code

class InteractiveInterpreter(code.InteractiveConsole):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent  # Reference to the main agent instance
        self.commands = {
            "add_task": self.add_task,
            "run_tasks": self.run_tasks,
            "add_module": self.add_module,
        }

    def start(self):
        banner = "Welcome to Agent-A Interactive Interpreter. Type your commands below."
        self.interact(banner)

    def add_task(self, task):
        self.agent.decision_maker.add_task(task)
        print(f"Task '{task.__name__}' added.")

    def run_tasks(self):
        self.agent.decision_maker.execute_tasks()
        print("Running tasks...")

    def add_module(self, module):
        self.agent.modularity.add_module(module)
        print(f"Module '{module.__name__}' added.")

    def runsource(self, source, filename="<input>", symbol="single"):
        command = source.strip()
        if command in self.commands:
            self.commands[command]()
            return False  # Do not store the command in history
        else:
            return super().runsource(source, filename, symbol)