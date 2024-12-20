from .core import BaseAgent

class DecisionAgent(BaseAgent):
    def execute(self, task):
        print(f"Executing task: {task}")
        # Implement execution logic here
