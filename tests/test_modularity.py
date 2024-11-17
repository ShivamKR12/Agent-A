import unittest
from src.agent_a.modularity import Modularity

class TestModularity(unittest.TestCase):
    def setUp(self):
        self.modularity = Modularity()

    def test_initialization(self):
        self.assertIsNotNone(self.modularity)
        self.assertEqual(self.modularity.modules, [])

    def test_add_module(self):
        def sample_module():
            pass
        self.modularity.add_module(sample_module)
        self.assertEqual(len(self.modularity.modules), 1)
        self.assertEqual(self.modularity.modules[0], sample_module)

    def test_extend(self):
        self.execution_flag = False

        def sample_module():
            self.execution_flag = True

        self.modularity.add_module(sample_module)
        self.modularity.extend()
        self.assertTrue(self.execution_flag)

    def test_remove_module(self):
        def sample_module():
            pass
        self.modularity.add_module(sample_module)
        self.modularity.remove_module(sample_module)
        self.assertEqual(len(self.modularity.modules), 0)

if __name__ == '__main__':
    unittest.main()
