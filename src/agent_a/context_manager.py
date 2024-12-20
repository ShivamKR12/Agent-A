import psutil
import platform
from datetime import datetime

class ContextManager:
    def __init__(self, conversation_manager, state, config, logger):
        self.conversation_manager = conversation_manager
        self.state = state
        self.config = config
        self.logger = logger

    def _manage_context_module(self, context):
        """Core module for context management"""
        try:
            # Update conversation context
            conversation_context = self.conversation_manager.get_relevant_context(
                context.get("current_command", {}).get("command", "")
            )
            context.set("conversation_context", conversation_context)
            
            # Update system context
            system_context = {
                "timestamp": datetime.utcnow().isoformat(),
                "user": "ShivamKR12",
                "system_info": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "platform": platform.platform()
                }
            }
            context.set("system_context", system_context)
            
            # Manage memory and cleanup
            self._manage_memory(context)
            
        except Exception as e:
            self.logger.error(f"Error in context management: {e}")
            context.set("context_error", str(e))

    def _manage_memory(self, context):
        """Manage system memory and cleanup old data"""
        try:
            # Clean up old history if too large
            if len(self.state.command_history.history) > self.config.command_history_size:
                self.state.command_history.history.popleft()
                
            # Clean up old conversation history
            if len(self.conversation_manager.history) > 100:  # Configurable
                self.conversation_manager.history = self.conversation_manager.history[-100:]
                
        except Exception as e:
            self.logger.error(f"Error in memory management: {e}")
