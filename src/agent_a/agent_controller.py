from .interpreter_agent import OpenInterpreterAgent
from .decision_agent import DecisionAgent
from .modular_agent import ModularAgent

class UnifiedAgent:
    def __init__(self):
        self.interpreter = OpenInterpreterAgent()
        self.decision_maker = DecisionAgent()
        self.extender = ModularAgent()

    def process_command(self, command):
        parsed_command = self.interpreter.parse(command)
        self.decision_maker.execute(parsed_command)

    def add_extension(self, plugin):
        self.extender.extend(plugin)
