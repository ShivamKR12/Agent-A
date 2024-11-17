import code

class InteractiveInterpreter:
    def __init__(self):
        self.interpreter = code.InteractiveConsole()

    def start(self):
        self.interpreter.interact("Welcome to Agent-A Interactive Interpreter. Type your commands below.")
