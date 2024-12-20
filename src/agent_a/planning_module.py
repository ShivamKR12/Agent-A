import networkx as nx
from uuid import uuid4
from typing import Dict, Any, List

class PlanningModule:
    def __init__(self, logger):
        self.logger = logger

    def _planning_module(self, context: Dict[str, Any]):
        """Core module for planning and reasoning"""
        try:
            current_command = context.get("current_command", {})
            ai_response = context.get("ai_response", {})
            
            # Create or update execution plan
            plan = self._create_execution_plan(current_command, ai_response)
            
            # Validate plan
            if self._validate_plan(plan):
                context.set("execution_plan", plan)
                context.set("plan_status", "valid")
            else:
                context.set("plan_status", "invalid")
                context.set("plan_error", "Plan validation failed")
                
        except Exception as e:
            self.logger.error(f"Error in planning module: {e}")
            context.set("planning_error", str(e))

    def _create_execution_plan(self, command: Dict[str, Any], ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed execution plan"""
        plan = {
            "id": str(uuid4()),
            "created_at": "2024-12-20 07:15:26",
            "user": "ShivamKR12",
            "command": command.get("command", ""),
            "steps": [],
            "status": "created",
            "metadata": {
                "source": "Agent-A",
                "priority": "normal",
                "estimated_duration": 0
            }
        }
        
        # Extract actions from AI response
        actions = self._extract_actions(ai_response)
        
        # Convert actions to plan steps
        for idx, action in enumerate(actions):
            step = {
                "id": f"step_{idx}",
                "action": action,
                "dependencies": [],
                "status": "pending",
                "retry_count": 0,
                "max_retries": 3
            }
            
            # Add step dependencies
            if idx > 0:
                step["dependencies"].append(f"step_{idx-1}")
                
            plan["steps"].append(step)
            
        # Estimate plan duration
        plan["metadata"]["estimated_duration"] = len(plan["steps"]) * 5  # 5 seconds per step
        
        return plan

    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate execution plan"""
        try:
            # Check required fields
            required_fields = ["id", "created_at", "steps", "status"]
            for field in required_fields:
                if field not in plan:
                    return False
                    
            # Check steps
            for step in plan["steps"]:
                if "id" not in step or "action" not in step:
                    return False
                    
            # Check for circular dependencies
            if self._has_circular_dependencies(plan["steps"]):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating plan: {e}")
            return False

    def _has_circular_dependencies(self, steps: List[Dict[str, Any]]) -> bool:
        """Check for circular dependencies in plan steps"""
        graph = nx.DiGraph()
        
        # Build dependency graph
        for step in steps:
            graph.add_node(step["id"])
            for dep in step.get("dependencies", []):
                graph.add_edge(step["id"], dep)
                
        try:
            # Check for cycles
            nx.find_cycle(graph)
            return True
        except nx.NetworkXNoCycle:
            return False
