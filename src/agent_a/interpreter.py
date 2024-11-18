import code

class InteractiveInterpreter:
    def __init__(self):
        self.interpreter = code.InteractiveConsole()
        self.running = True

    def start(self):
        self.interpreter.interact("Welcome to Agent-A Interactive Interpreter. Type your commands below.")
        
    def stop(self):
        """Stop the interpreter gracefully"""
        self.running = False
