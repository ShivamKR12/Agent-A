from agent_a import UnifiedAgent

if __name__ == "__main__":
    agent = UnifiedAgent()
    agent.process_command("Translate: Hello World")
    agent.add_extension("NewPlugin")
