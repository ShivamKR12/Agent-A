import re
from typing import List, Dict, Any

class ActionExtractor:
    def __init__(self, logger):
        self.logger = logger

    def _extract_actions(self, ai_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable items from AI response"""
        try:
            content = ai_response["content"]
            actions = []
            
            # Extract code blocks
            code_blocks = self._extract_code_blocks(content)
            for block in code_blocks:
                actions.append({
                    "type": "code_execution",
                    "language": block["language"],
                    "code": block["code"],
                    "timestamp": "2024-12-20 07:15:26",
                    "priority": "high" if block["language"] in ["python", "shell"] else "medium"
                })
                
            # Extract system commands
            system_commands = self._extract_system_commands(content)
            for cmd in system_commands:
                actions.append({
                    "type": "system_command",
                    "command": cmd,
                    "timestamp": "2024-12-20 07:15:26",
                    "priority": "high"
                })
                
            # Extract file operations
            file_ops = self._extract_file_operations(content)
            for op in file_ops:
                actions.append({
                    "type": "file_operation",
                    "operation": op["operation"],
                    "path": op["path"],
                    "timestamp": "2024-12-20 07:15:26",
                    "priority": "medium"
                })
                
            return actions
                
        except Exception as e:
            self.logger.error(f"Error extracting actions: {e}")
            return []

    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
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

    def _extract_system_commands(self, content: str) -> List[str]:
        """Extract system commands from content"""
        commands = []
        # Look for shell command patterns
        patterns = [
            r"\$\s*(.*?)(?=\n|$)",  # Commands starting with $
            r"#!/.*?\n(.*?)(?=\n```|$)",  # Shell scripts
            r"sudo\s+(.*?)(?=\n|$)"  # sudo commands
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                cmd = match.group(1).strip()
                if cmd:
                    commands.append(cmd)
                    
        return commands

    def _extract_file_operations(self, content: str) -> List[Dict[str, Any]]:
        """Extract file operations from content"""
        operations = []
        # Look for file operation patterns
        file_patterns = {
            "read": r"(?:read|open|cat)\s+[\"']?([\w./]+)[\"']?",
            "write": r"(?:write|save|create)\s+(?:to\s+)?[\"']?([\w./]+)[\"']?",
            "delete": r"(?:delete|remove|rm)\s+[\"']?([\w./]+)[\"']?",
            "modify": r"(?:modify|update|change)\s+[\"']?([\w./]+)[\"']?"
        }
        
        for op_type, pattern in file_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                path = match.group(1)
                operations.append({
                    "operation": op_type,
                    "path": path
                })
                
        return operations
