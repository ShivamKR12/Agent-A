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

if __name__ == '__main__':
    unittest.main()
