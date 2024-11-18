class MemorySystem:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.memory = []

    def store_interaction(self, query: str, response: str):
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)  # Remove the oldest interaction
        self.memory.append({'query': query, 'response': response})

    def retrieve_memory(self):
        return self.memory

    def clear_memory(self):
        self.memory = []
