import unittest
from src.agent_a.decision_maker import DecisionMaker

class TestDecisionMaker(unittest.TestCase):
    def setUp(self):
        self.decision_maker = DecisionMaker()

    def test_initialization(self):
        self.assertIsNotNone(self.decision_maker)
        self.assertFalse(self.decision_maker.running)
        self.assertEqual(self.decision_maker.tasks, [])

    def test_add_task(self):
        def sample_task():
            pass
        self.decision_maker.add_task(sample_task)
        self.assertEqual(len(self.decision_maker.tasks), 1)
        self.assertEqual(self.decision_maker.tasks[0], sample_task)

    def test_execute_tasks(self):
        self.execution_flag = False

        def sample_task():
            self.execution_flag = True

        self.decision_maker.add_task(sample_task)
        self.decision_maker.execute_tasks()
        self.assertTrue(self.execution_flag)

    def test_stop(self):
        self.decision_maker.start()
        self.decision_maker.stop()
        self.assertFalse(self.decision_maker.running)

if __name__ == '__main__':
    unittest.main()
