import openai
import logging
from src.agent_a.memory import MemorySystem
from src.agent_a.knowledge_base import KnowledgeBase
from src.agent_a.decision_maker import DecisionMaker

class AgentBrain:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        openai.api_key = self.config.get('openai_api_key')

        self.memory = MemorySystem()
        self.knowledge_base = KnowledgeBase()
        self.decision_maker = DecisionMaker()

    def process_query(self, query: str) -> str:
        context = self.knowledge_base.retrieve_context(query)
        reasoning_steps = self.decision_maker.plan_reasoning(query)

        # Generate response
        response = self._generate_response(query, context, reasoning_steps)
        self.memory.store_interaction(query, response)

        return response

    def _generate_response(self, query, context, reasoning_steps):
        openai_response = self._get_openai_response(query, context)
        # You can add local model responses here if needed
        return openai_response

    def _get_openai_response(self, query, context):
        try:
            response = openai.ChatCompletion.create(
                model=self.config.get('openai_model', 'gpt-4'),
                messages=[{"role": "user", "content": query}]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return "I'm sorry, I couldn't process your request."
