import logging
from src.agent_a.interpreter import InteractiveInterpreter
from src.agent_a.decision_maker import DecisionMaker
from src.agent_a.modularity import Modularity

class AgentA:
    def __init__(self):
        self.interpreter = InteractiveInterpreter()
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
            self.decision_maker.execute_tasks()
            self.modularity.extend()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise

if __name__ == "__main__":
    agent = AgentA()
    agent.run()
