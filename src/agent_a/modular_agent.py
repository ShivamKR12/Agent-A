from .core import BaseAgent

class ModularAgent(BaseAgent):
    def extend(self, plugin):
        print(f"Adding plugin: {plugin}")
        # Implement plugin logic here
