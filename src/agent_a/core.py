import logging
from agent_a.open_interpreter.interpreter import InteractiveInterpreter
from agent_a.agent_zero.decision_maker import DecisionMaker
from agent_a.agent_k.modularity import Modularity

class AgentA:
    def __init__(self):
        self.interpreter = InteractiveInterpreter(self)
        self.decision_maker = DecisionMaker()
        self.modularity = Modularity()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run(self):
        try:
            self.logger.info("Starting Agent-A")
            self.interpreter.start()
            self.logger.info("Interpreter started")
            self.decision_maker.start()
            self.logger.info("Decision maker started executing tasks")
            # Add an example module
            self.modularity.add_module(self.example_module)
            self.modularity.extend()
            self.logger.info("Modules extended")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise

    def example_module(self):
        print("Example module executed")

if __name__ == "__main__":
    agent = AgentA()
    agent.run()