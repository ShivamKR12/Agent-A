import unittest
from unittest.mock import patch
from src.agent_a.core import AgentA

class TestAgentA(unittest.TestCase):
    def setUp(self):
        self.agent = AgentA()

    def test_initialization(self):
        self.assertIsNotNone(self.agent.interpreter)
        self.assertIsNotNone(self.agent.decision_maker)
        self.assertIsNotNone(self.agent.modularity)

    @patch('builtins.input', side_effect=['exit'])
    def test_run(self, mock_input):
        try:
            self.agent.run()
        except Exception as e:
            self.fail(f"AgentA run method raised an exception: {e}")

    def test_register_core_modules(self):
        self.agent.initialize_components()
        self.assertIn("command_processor", self.agent.modularity.modules)
        self.assertIn("result_handler", self.agent.modularity.modules)

    def test_command_processing(self):
        self.agent.initialize_components()
        self.agent._command_handler("test_command")
        task_ids = self.agent.modularity.context.get("task_ids")
        self.assertIsNotNone(task_ids)
        self.assertGreater(len(task_ids), 0)

    def test_result_handling(self):
        self.agent.initialize_components()
        self.agent._command_handler("test_command")
        self.agent.decision_maker.start()
        time.sleep(1)  # Allow some time for the tasks to execute
        self.agent.decision_maker.stop()
        results = self.agent.modularity.context.get("results")
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

if __name__ == '__main__':
    unittest.main()
