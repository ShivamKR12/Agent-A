from typing import List, Dict, Any

class ResponseGenerator:
    def __init__(self, logger):
        self.logger = logger

    def _generate_response_module(self, context: Dict[str, Any]):
        """Core module for response generation"""
        try:
            # Get relevant information from context
            execution_results = context.get("processed_execution_results", [])
            plan_status = context.get("plan_status")
            ai_response = context.get("ai_response", {})
            
            # Generate appropriate response
            response = self._format_response(
                execution_results,
                plan_status,
                ai_response
            )
            
            context.set("command_response", response)
            
        except Exception as e:
            self.logger.error(f"Error in response generation: {e}")
            context.set("response_error", str(e))

    def _format_response(self, execution_results: List[Dict[str, Any]], 
                        plan_status: str,
                        ai_response: Dict[str, Any]) -> str:
        """Format the final response"""
        response_parts = []
        
        # Add AI response if available
        if ai_response.get("content"):
            response_parts.append(ai_response["content"])
            
        # Add execution results
        if execution_results:
            response_parts.append("\nExecution Results:")
            for result in execution_results:
                if result["success"]:
                    response_parts.append(
                        f"\n✓ {result['language']} execution successful:"
                        f"\n{result['output']}"
                    )
                else:
                    response_parts.append(
                        f"\n✗ {result['language']} execution failed:"
                        f"\n{result['error']}"
                    )
                    
        # Add plan status
        if plan_status:
            response_parts.append(f"\nPlan Status: {plan_status}")
            
        return "\n".join(response_parts)
