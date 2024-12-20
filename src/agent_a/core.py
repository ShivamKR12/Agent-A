import logging
import signal
import sys
import time
from typing import Optional, Dict, Any
from agent_a.open_interpreter.interpreter import InteractiveInterpreter
from agent_a.agent_zero.decision_maker import DecisionMaker
from agent_a.agent_k.modularity import Modularity, Module

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
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _register_core_modules(self):
        """Register core functionality modules"""
        # Command processing module
        self.modularity.register_module(Module(
            name="command_processor",
            execute=self._process_command_module,
            provides=["command_processing"]
        ))

        # Result handling module
        self.modularity.register_module(Module(
            name="result_handler",
            execute=self._handle_result_module,
            dependencies=["command_processing"],
            provides=["result_handling"]
        ))

    def _process_command_module(self, context: Dict[str, Any]):
        """Core module for processing commands"""
        command = context.get("current_command")
        if command:
            # Create reasoning plan
            task_ids = self.decision_maker.create_reasoning_plan(command)
            context["task_ids"] = task_ids

    def _handle_result_module(self, context: Dict[str, Any]):
        """Core module for handling results"""
        task_ids = context.get("task_ids", [])
        results = []
        
        for task_id in task_ids:
            result = self.decision_maker.get_task_result(task_id)
            if result:
                results.append(result)
                
        context["results"] = results

    def _command_handler(self, command: str):
        """Handle commands from the interpreter"""
        self.modularity.context.set("current_command", command)
        self.modularity.extend()

    def initialize_components(self):
        """Initialize all components with proper error handling"""
        try:
            self.interpreter = InteractiveInterpreter(self)
            self.decision_maker = DecisionMaker()
            self.modularity = Modularity()
            self._register_core_modules()
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise

    def run(self):
        """Main execution loop"""
        try:
            self.logger.info("Starting Agent-A")
            self.initialize_components()
            
            if not all([self.interpreter, self.decision_maker, self.modularity]):
                raise RuntimeError("Components not properly initialized")

            # Start decision maker in background
            self.decision_maker.start()
            
            # Register interpreter commands as decision maker tasks
            self.interpreter.set_command_handler(self._command_handler)
            
            # Start interpreter (non-blocking)
            self.interpreter.start_async()
            
            # Main loop
            self.running = True
            while self.running:
                time.sleep(0.1)  # Prevent CPU spinning
                
        except Exception as e:
            self.logger.error(f"Critical error during execution: {e}")
            self.cleanup()
            raise
        finally:
            self.cleanup()

    def stop(self):
        """Stop all components"""
        if self.interpreter:
            self.interpreter.stop()
        if self.decision_maker:
            self.decision_maker.stop()
        if self.modularity:
            self.modularity.cleanup()

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, stopping AgentA...")
        self.stop()
        sys.exit(0)
