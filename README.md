# Agent-A
An Agentic AI

## Project Goals

### Combine Functionalities
Integrate the core features of OpenInterpreter, Agent Zero, and AgentK into a single unified AI agent.

### Error Minimization
Ensure robust error handling and modular design to facilitate debugging and future scalability.

## Key Features

- Interactive interpreter (from OpenInterpreter).
- Autonomous decision-making and task execution (from Agent Zero).
- Modularity and extendibility (from AgentK).

## Installation Instructions

1. Clone the repository:
   ```sh
   git clone https://github.com/ShivamKR12/Agent-A.git
   cd Agent-A
   ```

2. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage Instructions

1. Activate the virtual environment:
   ```sh
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Run the agent:
   ```sh
   python src/agent_a/core.py
   ```

## Unified Agent

Import the `UnifiedAgent` to access all functionalities:
```python
from agent_a import UnifiedAgent

agent = UnifiedAgent()
agent.process_command("Command Here")
agent.add_extension("PluginName")
```

## Contribution Guidelines

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.
