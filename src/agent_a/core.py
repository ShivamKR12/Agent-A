import logging
import signal
import sys
from typing import Optional
from src.agent_a.interpreter import InteractiveInterpreter
from src.agent_a.decision_maker import DecisionMaker
from src.agent_a.modularity import Modularity

class AgentA:
    def __init__(self):
        self._setup_logging()
        self.running = False
        self.interpreter: Optional[InteractiveInterpreter] = None
        self.decision_maker: Optional[DecisionMaker] = None
        self.modularity: Optional[Modularity] = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Setup logging with proper configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Remove existing handlers to prevent duplicates
        self.logger.handlers.clear()
        
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def initialize_components(self):
        """Initialize all components with proper error handling"""
        try:
            self.interpreter = InteractiveInterpreter()
            self.decision_maker = DecisionMaker()
            self.modularity = Modularity()
            self.running = True
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def run(self):
        """Main execution loop with proper error handling"""
        try:
            self.logger.info("Starting Agent-A")
            self.initialize_components()
            
            if not all([self.interpreter, self.decision_maker, self.modularity]):
                raise RuntimeError("Components not properly initialized")

            self.interpreter.start()
            self.decision_maker.execute_tasks()
            self.modularity.extend()
            
        except Exception as e:
            self.logger.error(f"Critical error during execution: {e}")
            self.cleanup()
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources and shutdown gracefully"""
        self.logger.info("Shutting down Agent-A")
        self.running = False
        
        try:
            if self.interpreter:
                self.interpreter.stop()
            if self.decision_maker:
                self.decision_maker.stop()
            if self.modularity:
                self.modularity.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _signal_handler(self, signum, frame):
        """Handle system signals gracefully"""
        self.logger.info(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)

if __name__ == "__main__":
    agent = AgentA()
    try:
        agent.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
