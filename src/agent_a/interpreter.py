import code
import threading
import queue
import logging
from typing import Callable, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
import os
import json
import psutil
import platform

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

    def _handle_command(self, command: str):
        """Handle commands from the interpreter"""
        try:
            # Add command to history
            self.agent.state.command_history.add_command(command, {
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
            self.agent.decision_maker.add_task(task, callback=self._command_completed)
            
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")

    def _process_command(self, context: dict) -> dict:
        """Process a command through the module system"""
        try:
            # Update shared context
            self.agent.modularity.context.set("current_command", context)
            
            # Execute module chain
            self.agent.modularity.extend()
            
            # Get response from context
            response = self.agent.modularity.context.get("command_response")
            
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

    def _handle_built_in_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle built-in commands starting with /"""
        cmd_parts = command[1:].split()
        cmd_name = cmd_parts[0].lower()
        cmd_args = cmd_parts[1:]
        
        built_in_commands = {
            "help": self._cmd_help,
            "exit": self._cmd_exit,
            "clear": self._cmd_clear,
            "history": self._cmd_history,
            "status": self._cmd_status,
            "capabilities": self._cmd_capabilities,
            "execute": self._cmd_execute,
            "plan": self._cmd_plan,
            "modules": self._cmd_modules
        }
        
        if cmd_name in built_in_commands:
            return built_in_commands[cmd_name](cmd_args, context)
        else:
            raise ValueError(f"Unknown command: {cmd_name}")

    def _cmd_help(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Show help information"""
        help_text = """
        Available Commands:
        /help         - Show this help message
        /exit        - Exit the agent
        /clear       - Clear the screen
        /history     - Show command history
        /status      - Show agent status
        /capabilities- List agent capabilities
        /execute     - Execute code directly
        /plan        - Show or create execution plan
        /modules     - List loaded modules
        
        Code Execution:
        You can execute code by using ```language
        For example:
        ```python
        print("Hello, World!")
        ```
        
        Supported Languages:
        - Python
        - JavaScript
        - Shell
        - AppleScript
        - R
        - SQL
        """
        return {
            "status": "success",
            "response": help_text,
            "command_context": context
        }

    def _cmd_exit(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Exit the agent"""
        self.agent.cleanup()
        return {
            "status": "success",
            "response": "Exiting Agent-A...",
            "command_context": context,
            "should_exit": True
        }

    def _cmd_clear(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return {
            "status": "success",
            "response": "",
            "command_context": context
        }

    def _cmd_history(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Show command history"""
        n = int(args[0]) if args else 10
        history = self.agent.state.command_history.get_last_n_commands(n)
        
        response = "Command History:\n"
        for entry in history:
            response += f"{entry['timestamp']}: {entry['command']}\n"
            
        return {
            "status": "success",
            "response": response,
            "command_context": context
        }

    def _cmd_status(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Show agent status"""
        status = {
            "running": self.agent.running,
            "active_tasks": len(self.agent.decision_maker.active_tasks),
            "loaded_modules": len(self.agent.modularity.modules),
            "conversation_messages": len(self.agent.conversation_manager.history),
            "system_info": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "python_version": platform.python_version(),
                "platform": platform.platform()
            }
        }
        
        return {
            "status": "success",
            "response": json.dumps(status, indent=2),
            "command_context": context
        }

    def _cmd_capabilities(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """List agent capabilities"""
        return {
            "status": "success",
            "response": json.dumps(self.agent.capabilities.capabilities, indent=2),
            "command_context": context
        }

    def _cmd_execute(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code directly"""
        if len(args) < 2:
            raise ValueError("Usage: /execute <language> <code>")
            
        language = args[0]
        code = " ".join(args[1:])
        
        result = self.agent.code_executor.execute_code(code, language, context)
        return {
            "status": "success" if result["success"] else "error",
            "response": result["output"] if result["success"] else result["error"],
            "command_context": context
        }

    def _cmd_plan(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Show or create execution plan"""
        if not args:
            # Show current plan
            if self.agent.planning_system.current_plan:
                return {
                    "status": "success",
                    "response": json.dumps(self.agent.planning_system.current_plan, indent=2),
                    "command_context": context
                }
            else:
                return {
                    "status": "success",
                    "response": "No active plan",
                    "command_context": context
                }
        else:
            # Create new plan
            goal = " ".join(args)
            plan = self.agent.planning_system.create_plan(goal, context)
            return {
                "status": "success",
                "response": json.dumps(plan, indent=2),
                "command_context": context
            }

    def _cmd_modules(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """List loaded modules"""
        modules = [{
            "name": name,
            "provides": module.provides,
            "dependencies": module.dependencies
        } for name, module in self.agent.modularity.modules.items()]
        
        return {
            "status": "success",
            "response": json.dumps(modules, indent=2),
            "command_context": context
        }
