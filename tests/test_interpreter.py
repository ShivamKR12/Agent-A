import unittest
from unittest.mock import patch, MagicMock
from src.agent_a.interpreter import InteractiveInterpreter

class TestInteractiveInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = InteractiveInterpreter()

    def test_initialization(self):
        self.assertIsNotNone(self.interpreter)

    @patch('builtins.input', side_effect=['exit'])
    def test_start(self, mock_input):
        try:
            self.interpreter.start_async()
        except Exception as e:
            self.fail(f"InteractiveInterpreter start method raised an exception: {e}")

    def test_non_blocking_operation(self):
        self.interpreter.start_async()
        self.assertTrue(self.interpreter.running)
        self.interpreter.stop()
        self.assertFalse(self.interpreter.running)

    def test_command_handler(self):
        mock_handler = MagicMock()
        self.interpreter.set_command_handler(mock_handler)
        self.interpreter.start_async()
        self.interpreter.command_queue.put("test_command")
        self.interpreter._process_loop()
        mock_handler.assert_called_with("test_command")
        self.interpreter.stop()

if __name__ == '__main__':
    unittest.main()
