from typing import List, Dict, Any, Optional
from collections import deque
import json
import threading
from datetime import datetime

class CommandHistory:
    def __init__(self, max_size: int = 1000):
        self.history = deque(maxlen=max_size)
        self._lock = threading.Lock()

    def add_command(self, command: str, context: Dict[str, Any]):
        """Add a command to history with its context"""
        with self._lock:
            entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'command': command,
                'context': context
            }
            self.history.append(entry)

    def get_last_n_commands(self, n: int) -> List[Dict[str, Any]]:
        """Get the last n commands from history"""
        with self._lock:
            return list(self.history)[-n:]

    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Search command history for matching commands"""
        with self._lock:
            return [
                entry for entry in self.history
                if query.lower() in entry['command'].lower()
            ]

class AgentState:
    def __init__(self, config: 'AgentConfig'):
        self.config = config
        self.command_history = CommandHistory(config.command_history_size)
        self._state = {}
        self._lock = threading.Lock()
        self._state_file = Path(config.data_dir) / "agent_state.json"
        self._load_state()

    def _load_state(self):
        """Load state from disk if it exists"""
        try:
            if self._state_file.exists():
                with open(self._state_file, 'r') as f:
                    self._state = json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")

    def _save_state(self):
        """Save current state to disk"""
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._state_file, 'w') as f:
                json.dump(self._state, f)
        except Exception as e:
            print(f"Error saving state: {e}")

    def set(self, key: str, value: Any):
        """Set a state value"""
        with self._lock:
            self._state[key] = value
            self._save_state()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value"""
        with self._lock:
            return self._state.get(key, default)

    def update(self, updates: Dict[str, Any]):
        """Update multiple state values"""
        with self._lock:
            self._state.update(updates)
            self._save_state()
