from dataclasses import dataclass
from typing import Dict, Any
import yaml
import os

@dataclass
class AgentConfig:
    max_workers: int = 4
    task_timeout: int = 60
    log_level: str = "INFO"
    command_history_size: int = 1000
    module_auto_reload: bool = True
    interpreter_prompt: str = ">>> "
    
    # System paths
    data_dir: str = "./data"
    log_dir: str = "./logs"
    module_dir: str = "./modules"
    
    # Integration settings
    enable_api_server: bool = False
    api_port: int = 8080
    api_host: str = "localhost"

    @classmethod
    def from_yaml(cls, path: str) -> 'AgentConfig':
        if os.path.exists(path):
            with open(path, 'r') as f:
                config_dict = yaml.safe_load(f)
                return cls(**config_dict)
        return cls()
