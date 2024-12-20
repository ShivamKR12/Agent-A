from .core import BaseAgent

class OpenInterpreterAgent(BaseAgent):
    def parse(self, command):
        print(f"Parsing command: {command}")
        # Implement parsing logic here
