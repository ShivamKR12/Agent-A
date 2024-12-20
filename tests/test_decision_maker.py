import unittest
from src.agent_a.decision_maker import DecisionMaker, TaskStatus

class TestDecisionMaker(unittest.TestCase):
    def setUp(self):
        self.decision_maker = DecisionMaker()

    def test_initialization(self):
        self.assertIsNotNone(self.decision_maker)
        self.assertFalse(self.decision_maker.running)
        self.assertEqual(len(self.decision_maker.active_tasks), 0)

    def test_add_task(self):
        def sample_task(context):
            return "task_result"
        task_id = self.decision_maker.add_task(sample_task)
        self.assertEqual(len(self.decision_maker.active_tasks), 1)
        self.assertEqual(self.decision_maker.active_tasks[task_id].callable, sample_task)

    def test_execute_tasks(self):
        self.execution_flag = False

        def sample_task(context):
            self.execution_flag = True
            return "task_result"

        task_id = self.decision_maker.add_task(sample_task)
        self.decision_maker.start()
        time.sleep(1)  # Allow some time for the task to execute
        self.decision_maker.stop()
        self.assertTrue(self.execution_flag)
        self.assertEqual(self.decision_maker.get_task_status(task_id), TaskStatus.COMPLETED)
        self.assertEqual(self.decision_maker.get_task_result(task_id), "task_result")

    def test_task_dependencies(self):
        self.execution_order = []

        def task_a(context):
            self.execution_order.append("A")
            return "result_a"

        def task_b(context):
            self.execution_order.append("B")
            return "result_b"

        task_a_id = self.decision_maker.add_task(task_a)
        task_b_id = self.decision_maker.add_task(task_b, dependencies=[task_a_id])
        self.decision_maker.start()
        time.sleep(2)  # Allow some time for the tasks to execute
        self.decision_maker.stop()
        self.assertEqual(self.execution_order, ["A", "B"])
        self.assertEqual(self.decision_maker.get_task_status(task_a_id), TaskStatus.COMPLETED)
        self.assertEqual(self.decision_maker.get_task_status(task_b_id), TaskStatus.COMPLETED)

    def test_context_handling(self):
        def sample_task(context):
            return {"key": "value"}

        task_id = self.decision_maker.add_task(sample_task)
        self.decision_maker.start()
        time.sleep(1)  # Allow some time for the task to execute
        self.decision_maker.stop()
        self.assertEqual(self.decision_maker.context.get("key"), "value")

    def test_error_handling(self):
        def failing_task(context):
            raise ValueError("Task failed")

        task_id = self.decision_maker.add_task(failing_task)
        self.decision_maker.start()
        time.sleep(1)  # Allow some time for the task to execute
        self.decision_maker.stop()
        self.assertEqual(self.decision_maker.get_task_status(task_id), TaskStatus.FAILED)
        self.assertIsInstance(self.decision_maker.active_tasks[task_id].error, ValueError)

if __name__ == '__main__':
    unittest.main()
