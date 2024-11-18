import openai
import logging
from typing import Optional, Dict, Any
from src.agent_a.memory import MemorySystem
from src.agent_a.knowledge_base import KnowledgeBase
from src.agent_a.decision_maker import DecisionMaker

class AgentBrain:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Validate OpenAI API key
        if not self.config.get('openai_api_key'):
            raise ValueError("OpenAI API key is required in config")
        
        try:
            openai.api_key = self.config['openai_api_key']
            self.memory = MemorySystem()
            self.knowledge_base = KnowledgeBase()
            self.decision_maker = DecisionMaker()
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise

    def process_query(self, query: str) -> str:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
            
        try:
            context = self.knowledge_base.retrieve_context(query)
            reasoning_steps = self.decision_maker.plan_reasoning(query)
            response = self._generate_response(query, context, reasoning_steps)
            self.memory.store_interaction(query, response)
            return response
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return "I apologize, but I encountered an error processing your request."

    def _generate_response(self, query: str, context: list, reasoning_steps: list) -> str:
        try:
            openai_response = self._get_openai_response(query, context)
            return openai_response
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            raise

    def _get_openai_response(self, query: str, context: list) -> str:
        try:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": f"Context: {context}\nQuery: {query}"}
            ]
            
            response = openai.ChatCompletion.create(
                model=self.config.get('openai_model', 'gpt-4'),
                messages=messages,
                timeout=30  # Add timeout
            )
            
            if not response.get('choices'):
                raise ValueError("No response choices returned from OpenAI")
                
            return response['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.memory.cleanup()
            self.knowledge_base.cleanup()
            self.decision_maker.stop()
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
