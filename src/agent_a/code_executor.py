import psutil
from typing import Dict, Any
from datetime import datetime

class CodeExecutor:
    def __init__(self, logger):
        self.logger = logger

    def _execute_code_module(self, context: Dict[str, Any]):
        """Core module for code execution"""
        try:
            # Get code execution results from context
            results = context.get("code_execution_results", [])
            
            if not results:
                return
                
            # Process each result
            processed_results = []
            for result in results:
                processed_result = self._process_execution_result(result)
                processed_results.append(processed_result)
                
            # Update context with processed results
            context.set("processed_execution_results", processed_results)
            
        except Exception as e:
            self.logger.error(f"Error in code execution module: {e}")
            context.set("execution_error", str(e))

    def _process_execution_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance code execution results"""
        try:
            enhanced_result = {
                "success": result.get("success", False),
                "language": result.get("language", "unknown"),
                "code": result.get("code", ""),
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "execution_time": result.get("execution_time", 0),
                "timestamp": "2024-12-20 07:15:26",
                "user": "ShivamKR12"
            }
            
            # Add additional metadata
            enhanced_result.update({
                "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024,  # MB
                "cpu_percent": psutil.Process().cpu_percent(),
                "system_load": psutil.getloadavg()[0]
            })
            
            # Add security check results
            security_check = self._check_code_security(result.get("code", ""))
            enhanced_result["security_check"] = security_check
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Error processing execution result: {e}")
            return result

    def _check_code_security(self, code: str) -> Dict[str, Any]:
        """Perform security checks on code"""
        security_results = {
            "safe": True,
            "warnings": [],
            "blocked_operations": []
        }
        
        # Check for dangerous operations
        dangerous_patterns = {
            "system_access": r"os\.|subprocess\.|system|exec",
            "file_operations": r"open\(|write|delete|remove",
            "network_access": r"socket\.|urllib|requests\.|http",
            "code_execution": r"eval|exec|compile",
            "shell_injection": r"shell=True|subprocess\.call"
        }
        
        for category, pattern in dangerous_patterns.items():
            if re.search(pattern, code):
                security_results["warnings"].append(f"Potential {category} detected")
                security_results["safe"] = False
                
        return security_results
