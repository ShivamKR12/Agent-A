import yaml
import logging
from src.agent_a.agent_brain import AgentBrain

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    config = load_config('configs/agent_config.yaml')
    
    # Initialize Agent
    agent = AgentBrain(config)
    
    # Interactive Loop
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            response = agent.process_query(user_input)
            print(f"Agent: {response}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
