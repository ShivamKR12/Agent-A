import logging
from agent_a.open_interpreter.interpreter import InteractiveInterpreter
from agent_a.agent_zero.decision_maker import DecisionMaker
from agent_a.agent_k.modularity import Modularity

class AgentA:
    def __init__(self):
        self.interpreter = InteractiveInterpreter(self)
        self.decision_maker = DecisionMaker()
        self.modularity = Modularity()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run(self):
        try:
            self.logger.info("Starting Agent-A")
            self.interpreter.start()
            self.logger.info("Interpreter started")
            self.decision_maker.start()
            self.logger.info("Decision maker started executing tasks")
            # Add an example module
            self.modularity.add_module(self.example_module)
            self.modularity.extend()
            self.logger.info("Modules extended")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise

    def example_module(self):
        print("Example module executed")

    def _process_command_module(self, context):
        """Core module for command processing"""
        try:
            current_command = context.get("current_command")
            if not current_command:
                return
                
            # Parse command for code blocks
            code_blocks = self._extract_code_blocks(current_command["command"])
            
            if code_blocks:
                # Process code blocks
                results = []
                for block in code_blocks:
                    result = self.code_executor.execute_code(
                        block["code"],
                        block["language"],
                        current_command
                    )
                    results.append(result)
                context.set("code_execution_results", results)
            else:
                # Process as natural language command
                self._process_natural_language(current_command, context)

        except Exception as e:
            self.logger.error(f"Error in command processing: {e}")
            context.set("processing_error", str(e))

    def _extract_code_blocks(self, text):
        """Extract code blocks from text using markdown-style formatting"""
        code_blocks = []
        pattern = r"```(\w+)\n(.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            language = match.group(1).lower()
            code = match.group(2).strip()
            code_blocks.append({
                "language": language,
                "code": code
            })
            
        return code_blocks

    def _process_natural_language(self, command, context):
        """Process natural language commands using AI models"""
        try:
            # Get AI response
            ai_response = self._get_ai_response(command["command"])
            
            # Extract potential code or actions
            actions = self._extract_actions(ai_response)
            
            context.set("ai_response", ai_response)
            context.set("extracted_actions", actions)
            
        except Exception as e:
            self.logger.error(f"Error processing natural language: {e}")
            context.set("nl_processing_error", str(e))

if __name__ == "__main__":
    agent = AgentA()
    agent.run()
