import openai
import anthropic
from datetime import datetime

class AIResponseHandler:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def _get_ai_response(self, prompt: str) -> dict:
        """Get response from AI models"""
        try:
            # Try GPT-4 first
            if self.config.enable_gpt4:
                response = self._get_gpt4_response(prompt)
                if response:
                    return response

            # Fallback to Claude
            if self.config.enable_claude:
                response = self._get_claude_response(prompt)
                if response:
                    return response

            # Final fallback to simpler model
            return self._get_fallback_response(prompt)

        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            return {"error": str(e)}

    def _get_gpt4_response(self, prompt: str) -> dict:
        """Get response from GPT-4"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return {
                "model": "gpt-4",
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            self.logger.error(f"GPT-4 error: {e}")
            return None

    def _get_claude_response(self, prompt: str) -> dict:
        """Get response from Claude"""
        try:
            response = anthropic.completions.create(
                model="claude-2",
                prompt=f"{self._get_system_prompt()}\n\nHuman: {prompt}\n\nAssistant:",
                max_tokens_to_sample=2000
            )

            return {
                "model": "claude-2",
                "content": response.completion,
                "finish_reason": response.stop_reason
            }

        except Exception as e:
            self.logger.error(f"Claude error: {e}")
            return None

    def _get_fallback_response(self, prompt: str) -> dict:
        """Fallback response using simpler model or rule-based system"""
        # Implement fallback logic
        return {
            "model": "fallback",
            "content": "I apologize, but I'm currently operating in fallback mode."
        }

    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI models"""
        return """You are Agent-A, an advanced AI assistant that combines the capabilities of:
        1. Open Interpreter - For code execution and system operations
        2. Agent Zero - For conversation and context management
        3. Agent K - For planning and reasoning
        
        You can:
        - Execute code in multiple languages
        - Perform system operations
        - Manage files and data
        - Create and execute plans
        - Maintain context and memory
        - Learn from interactions
        
        Current timestamp: {timestamp}
        Current user: {user}
        
        Please provide clear, concise responses and always prioritize safety and security.""".format(
            timestamp=datetime.utcnow().isoformat(),
            user="ShivamKR12"
        )
