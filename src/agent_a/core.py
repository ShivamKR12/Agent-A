from .interpreter import InteractiveInterpreter
from .decision_maker import DecisionMaker
from .modularity import Modularity

class AgentA:
    def __init__(self):
        self.interpreter = InteractiveInterpreter(self)
        self.decision_maker = DecisionMaker()
        self.modularity = Modularity()

    def run(self):
        self.interpreter.start_async()
        self.decision_maker.start()

    def stop(self):
        self.interpreter.stop()
        self.decision_maker.stop()
        self.modularity.cleanup()
