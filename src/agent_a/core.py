import logging
import signal
import sys
import time
from typing import Optional, Dict, Any
from .interpreter import InteractiveInterpreter
from .decision_maker import DecisionMaker
from .modularity import Modularity, Module
from .config import AgentConfig
from .state import AgentState
from .api import APIServer

class AgentA:
    def __init__(self, config_path: str = None):
        self.config = AgentConfig.from_yaml(config_path or "config.yaml")
        self._setup_logging()
        self.state = AgentState(self.config)
        self.running = False
        self.interpreter: Optional[InteractiveInterpreter] = None
        self.decision_maker: Optional[DecisionMaker] = None
        self.modularity: Optional[Modularity] = None
        self.api_server: Optional[APIServer] = None

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

    def initialize_components(self):
        """Initialize all components with proper integration"""
        try:
            # Initialize base components with config
            self.interpreter = InteractiveInterpreter(
                prompt=self.config.interpreter_prompt
            )
            self.decision_maker = DecisionMaker(
                max_workers=self.config.max_workers
            )
            self.modularity = Modularity(
                auto_reload=self.config.module_auto_reload
            )
            
            # Initialize API server if enabled
            if self.config.enable_api_server:
                self.api_server = APIServer(self)
            
            # Register core modules
            self._register_core_modules()
            
            # Set up interpreter command handling
            self.interpreter.set_command_handler(self._handle_command)
            
            self.running = True
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def _register_core_modules(self):
        """Register the core functionality modules"""
        try:
            # Command Processing Module
            self.modularity.register_module(Module(
                name="command_processor",
                execute=self._process_command_module,
                provides=["command_processing"]
            ))
            
            # Context Management Module
            self.modularity.register_module(Module(
                name="context_manager",
                execute=self._manage_context_module,
                provides=["context_management"],
                dependencies=["command_processing"]
            ))
            
            # Response Generation Module
            self.modularity.register_module(Module(
                name="response_generator",
                execute=self._generate_response_module,
                dependencies=["context_management"]
            ))
            
        except Exception as e:
            self.logger.error(f"Failed to register core modules: {e}")
            raise

    def _handle_command(self, command: str):
        """Handle commands from the interpreter"""
        try:
            # Add command to history
            self.state.command_history.add_command(command, {
                "timestamp": datetime.utcnow().isoformat(),
                "user": "ShivamKR12"
            })
            
            # Create a unique task ID
            task_id = f"cmd_{uuid4().hex[:8]}"
            
            # Create command processing task
            task = Task(
                id=task_id,
                callable=self._process_command,
                priority=TaskPriority.HIGH,
                context={
                    "command": command,
                    "timestamp": time.time(),
                    "user": "ShivamKR12"  # Using the current user's login
                },
                timeout=30
            )
            
            # Add task to decision maker with callback
            self.decision_maker.add_task(task, callback=self._command_completed)
            
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")

    def _process_command(self, context: dict) -> dict:
        """Process a command through the module system"""
        try:
            # Update shared context
            self.modularity.context.set("current_command", context)
            
            # Execute module chain
            self.modularity.extend()
            
            # Get response from context
            response = self.modularity.context.get("command_response")
            
            return {
                "status": "success",
                "response": response,
                "command_context": context
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command_context": context
            }

    def _command_completed(self, result):
        """Handle command completion and response"""
        if result.success:
            response = result.result.get("response", "Command processed successfully")
            print(f"\n{response}\n>>> ", end="", flush=True)
        else:
            print(f"\nError: {result.error}\n>>> ", end="", flush=True)

    def _process_command_module(self, context):
        """Core module for command processing"""
        current_command = context.get("current_command")
        if current_command:
            # Process command logic here
            context.set("processed_command", {
                "parsed": True,
                "timestamp": time.time(),
                "command_type": "user_input"
            })

    def _manage_context_module(self, context):
        """Core module for context management"""
            processed_command = context.get("processed_command")
            if processed_command:
                # Update context with additional information
                context.set("command_context", {
                    "history": [],  # Add command history
                    "environment": {
                        "date": "2024-12-20",
                        "time": "06:53:16",
                        "user": "ShivamKR12"
                    }
                })

    def _generate_response_module(self, context):
        """Core module for response generation"""
        command_context = context.get("command_context")
        if command_context:
            # Generate appropriate response
            context.set("command_response", "Command processed successfully")

    def run(self):
        """Main execution loop with integrated component management"""
        try:
            self.logger.info("Starting Agent-A")
            self.initialize_components()
            
            if not all([self.interpreter, self.decision_maker, self.modularity]):
                raise RuntimeError("Components not properly initialized")

            # Start decision maker
            self.decision_maker.start()
            
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

    def cleanup(self):
        """Cleanup all components gracefully"""
        self.logger.info("Shutting down Agent-A")
        self.running = False
        
        try:
            # Stop components in reverse order
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
