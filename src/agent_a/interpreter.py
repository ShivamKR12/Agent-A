import code
import threading
import queue
import logging
from typing import Callable, Optional

class InteractiveInterpreter:
    def __init__(self, agent):
        self.agent = agent  # Reference to the main agent instance
        self.commands = {
            "add_task": self.add_task,
            "run_tasks": self.run_tasks,
            "add_module": self.add_module,
        }
        self.logger = logging.getLogger(__name__)
        self.interpreter = code.InteractiveConsole()
        self.running = False
        self.command_queue = queue.Queue()
        self.command_handler: Optional[Callable] = None
        self._input_thread: Optional[threading.Thread] = None
        self._process_thread: Optional[threading.Thread] = None

    def set_command_handler(self, handler: Callable[[str], None]):
        """Set the callback handler for processing commands"""
        self.command_handler = handler

    def start_async(self):
        """Start the interpreter in non-blocking mode"""
        self.running = True
        self._input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self._process_thread = threading.Thread(target=self._process_loop, daemon=True)
        
        self._input_thread.start()
        self._process_thread.start()
        
        self.logger.info("Interpreter started in async mode")

    def _input_loop(self):
        """Handle user input in a separate thread"""
        print("Welcome to Agent-A Interactive Interpreter. Type your commands below.")
        while self.running:
            try:
                # Get input without blocking main thread
                command = input(">>> ")
                if command.strip():
                    self.command_queue.put(command)
            except EOFError:
                self.stop()
                break
            except Exception as e:
                self.logger.error(f"Input error: {e}")

    def _process_loop(self):
        """Process commands in a separate thread"""
        while self.running:
            try:
                # Get command with timeout to allow checking running state
                command = self.command_queue.get(timeout=0.1)
                
                # Execute in interpreter context
                result = self._execute_command(command)
                
                # Pass to handler if set
                if self.command_handler:
                    self.command_handler(command)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Command processing error: {e}")

    def _execute_command(self, command: str) -> bool:
        """Execute a command in the interpreter context"""
        try:
            # Execute in interpreter context
            code_obj = self.interpreter.runsource(command)
            return code_obj is not None
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return False

    def stop(self):
        """Stop the interpreter gracefully"""
        self.running = False
        
        # Wait for threads to finish
        if self._input_thread and self._input_thread.is_alive():
            self._input_thread.join(timeout=1.0)
        if self._process_thread and self._process_thread.is_alive():
            self._process_thread.join(timeout=1.0)
            
        # Clear command queue
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break

        self.logger.info("Interpreter stopped")

    def add_task(self, task):
        self.agent.decision_maker.add_task(task)
        print(f"Task '{task.__name__}' added.")

    def run_tasks(self):
        self.agent.decision_maker.execute_tasks()
        print("Running tasks...")

    def add_module(self, module):
        self.agent.modularity.add_module(module)
        print(f"Module '{module.__name__}' added.")

    def runsource(self, source, filename="<input>", symbol="single"):
        command = source.strip()
        if command in self.commands:
            self.commands[command]()
            return False  # Do not store the command in history
        else:
            return super().runsource(source, filename, symbol)
