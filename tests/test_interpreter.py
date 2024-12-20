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

    def test_handle_built_in_command(self):
        context = {}
        response = self.interpreter._handle_built_in_command("/help", context)
        self.assertEqual(response["status"], "success")
        self.assertIn("Available Commands", response["response"])

    def test_cmd_help(self):
        context = {}
        response = self.interpreter._cmd_help([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("Available Commands", response["response"])

    def test_cmd_exit(self):
        context = {}
        response = self.interpreter._cmd_exit([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("Exiting Agent-A...", response["response"])

    def test_cmd_clear(self):
        context = {}
        with patch('os.system') as mock_system:
            response = self.interpreter._cmd_clear([], context)
            mock_system.assert_called_once()
            self.assertEqual(response["status"], "success")

    def test_cmd_history(self):
        context = {}
        self.agent.state.command_history.add_command("test_command", context)
        response = self.interpreter._cmd_history([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("test_command", response["response"])

    def test_cmd_status(self):
        context = {}
        response = self.interpreter._cmd_status([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("running", response["response"])

    def test_cmd_capabilities(self):
        context = {}
        self.agent.capabilities = MagicMock()
        self.agent.capabilities.capabilities = {"capability1": "description"}
        response = self.interpreter._cmd_capabilities([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("capability1", response["response"])

    def test_cmd_execute(self):
        context = {}
        self.agent.code_executor = MagicMock()
        self.agent.code_executor.execute_code.return_value = {"success": True, "output": "result"}
        response = self.interpreter._cmd_execute(["python", "print('Hello')"], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("result", response["response"])

    def test_cmd_plan(self):
        context = {}
        self.agent.planning_system = MagicMock()
        self.agent.planning_system.current_plan = {"plan": "details"}
        response = self.interpreter._cmd_plan([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("plan", response["response"])

    def test_cmd_modules(self):
        context = {}
        self.agent.modularity.modules = {"module1": MagicMock(provides=["feature"], dependencies=[])}
        response = self.interpreter._cmd_modules([], context)
        self.assertEqual(response["status"], "success")
        self.assertIn("module1", response["response"])

if __name__ == '__main__':
    unittest.main()
