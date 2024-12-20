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
        self.assertIn("context_manager", self.agent.modularity.modules)
        self.assertIn("response_generator", self.agent.modularity.modules)

    def test_command_processing(self):
        self.agent.initialize_components()
        self.agent._handle_command("test_command")
        task_ids = self.agent.modularity.context.get("current_command")
        self.assertIsNotNone(task_ids)

    def test_result_handling(self):
        self.agent.initialize_components()
        self.agent._handle_command("test_command")
        self.agent.decision_maker.start()
        time.sleep(1)  # Allow some time for the tasks to execute
        self.agent.decision_maker.stop()
        results = self.agent.modularity.context.get("command_response")
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()
