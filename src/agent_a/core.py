class BaseAgent:
    def parse(self, command):
        raise NotImplementedError

    def execute(self, task):
        raise NotImplementedError

    def extend(self, plugin):
        raise NotImplementedError
