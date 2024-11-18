class Modularity:
    def __init__(self):
        self.modules = []

    def add_module(self, module):
        self.modules.append(module)

    def extend(self):
        for module in self.modules:
            try:
                module()
            except Exception as e:
                print(f"Error executing module: {e}")

    def remove_module(self, module):
        if module in self.modules:
            self.modules.remove(module)
