import logging
import time
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

    # src/agent_a/core.py - Modified run() method
def run(self):
    """Main execution loop with proper integration"""
    try:
        self.logger.info("Starting Agent-A")
        self.initialize_components()
        
        if not all([self.interpreter, self.decision_maker, self.modularity]):
            raise RuntimeError("Components not properly initialized")

        # Start decision maker in background
        self.decision_maker.start()
        
        # Register interpreter commands as decision maker tasks
        def handle_command(cmd):
            self.decision_maker.add_task(lambda: self._process_command(cmd))
        self.interpreter.set_command_handler(handle_command)
        
        # Register core modules
        self.modularity.add_module(self._core_reasoning_module)
        self.modularity.add_module(self._core_learning_module)
        
        # Start interpreter (non-blocking)
        self.interpreter.start_async()
        
        # Main loop
        while self.running:
            time.sleep(0.1)  # Prevent CPU spinning
            
    except Exception as e:
        self.logger.error(f"Critical error during execution: {e}")
        self.cleanup()
        raise
    finally:
        self.cleanup()

def _process_command(self, cmd):
    """Process interpreter commands through decision maker"""
    try:
        # Create reasoning plan
        steps = self.decision_maker.plan_reasoning(cmd)
        
        # Execute reasoning steps
        self.decision_maker.execute_reasoning_plan(steps)
        
        # Allow modules to process result
        self.modularity.extend()
        
    except Exception as e:
        self.logger.error(f"Error processing command: {e}")

    def example_module(self):
        print("Example module executed")

if __name__ == "__main__":
    agent = AgentA()
    agent.run()