import unittest
from src.agent_a.core import AgentA

class TestAgentA(unittest.TestCase):
    def setUp(self):
        self.agent = AgentA()

    def test_initialization(self):
        self.assertIsNotNone(self.agent.interpreter)
        self.assertIsNotNone(self.agent.decision_maker)
        self.assertIsNotNone(self.agent.modularity)

    def test_run(self):
        try:
            self.agent.run()
        except Exception as e:
            self.fail(f"AgentA run method raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
