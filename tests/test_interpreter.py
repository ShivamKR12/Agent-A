import unittest
from src.agent_a.interpreter import InteractiveInterpreter

class TestInteractiveInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = InteractiveInterpreter()

    def test_initialization(self):
        self.assertIsNotNone(self.interpreter)

    def test_start(self):
        try:
            self.interpreter.start()
        except Exception as e:
            self.fail(f"InteractiveInterpreter start method raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
