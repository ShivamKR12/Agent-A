import unittest
from src.agent_a.modularity import Modularity, Module

class TestModularity(unittest.TestCase):
    def setUp(self):
        self.modularity = Modularity()

    def test_initialization(self):
        self.assertIsNotNone(self.modularity)
        self.assertEqual(self.modularity.modules, {})

    def test_register_module(self):
        def sample_module(context):
            pass
        module = Module(name="sample", execute=sample_module)
        self.modularity.register_module(module)
        self.assertEqual(len(self.modularity.modules), 1)
        self.assertEqual(self.modularity.modules["sample"], module)

    def test_unregister_module(self):
        def sample_module(context):
            pass
        module = Module(name="sample", execute=sample_module)
        self.modularity.register_module(module)
        self.modularity.unregister_module("sample")
        self.assertEqual(len(self.modularity.modules), 0)

    def test_extend(self):
        self.execution_flag = False

        def sample_module(context):
            self.execution_flag = True

        module = Module(name="sample", execute=sample_module)
        self.modularity.register_module(module)
        self.modularity.extend()
        self.assertTrue(self.execution_flag)

    def test_dependency_management(self):
        self.execution_order = []

        def module_a(context):
            self.execution_order.append("A")

        def module_b(context):
            self.execution_order.append("B")

        moduleA = Module(name="A", execute=module_a)
        moduleB = Module(name="B", execute=module_b, dependencies=["A"])

        self.modularity.register_module(moduleA)
        self.modularity.register_module(moduleB)
        self.modularity.extend()
        self.assertEqual(self.execution_order, ["A", "B"])

    def test_shared_context(self):
        def module_a(context):
            context.set("key", "value")

        def module_b(context):
            self.assertEqual(context.get("key"), "value")

        moduleA = Module(name="A", execute=module_a)
        moduleB = Module(name="B", execute=module_b, dependencies=["A"])

        self.modularity.register_module(moduleA)
        self.modularity.register_module(moduleB)
        self.modularity.extend()

if __name__ == '__main__':
    unittest.main()
