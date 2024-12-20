import unittest
from unittest.mock import patch, MagicMock
from src.agent_a.interpreter import InteractiveInterpreter
from src.agent_a.core import AgentA

class TestInteractiveInterpreter(unittest.TestCase):
    def setUp(self):
        self.agent = AgentA()
        self.interpreter = InteractiveInterpreter(self.agent)

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

    def test_add_task(self):
        def sample_task(context):
            return "task_result"
        self.interpreter.add_task(sample_task)
        self.assertEqual(len(self.agent.decision_maker.active_tasks), 1)

    def test_run_tasks(self):
        self.execution_flag = False

        def sample_task(context):
            self.execution_flag = True
            return "task_result"

        self.interpreter.add_task(sample_task)
        self.interpreter.run_tasks()
        self.assertTrue(self.execution_flag)

    def test_add_module(self):
        def sample_module(context):
            pass
        self.interpreter.add_module(sample_module)
        self.assertIn("sample_module", self.agent.modularity.modules)

if __name__ == '__main__':
    unittest.main()
