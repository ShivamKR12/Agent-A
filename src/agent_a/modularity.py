from typing import Dict, Any, Callable, List
import logging
from dataclasses import dataclass
import threading

@dataclass
class Module:
    name: str
    execute: Callable
    dependencies: List[str] = None
    provides: List[str] = None

class ModuleContext:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any):
        with self._lock:
            self._data[key] = value

    def get(self, key: str) -> Any:
        with self._lock:
            return self._data.get(key)

class Modularity:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.modules: Dict[str, Module] = {}
        self.context = ModuleContext()
        self._lock = threading.Lock()

    def register_module(self, module: Module):
        """Register a new module with dependency checking"""
        with self._lock:
            # Check dependencies
            if module.dependencies:
                missing = [dep for dep in module.dependencies if dep not in self.modules]
                if missing:
                    raise ValueError(f"Missing dependencies for module {module.name}: {missing}")
            
            self.modules[module.name] = module
            self.logger.info(f"Registered module: {module.name}")

    def unregister_module(self, name: str):
        """Unregister a module with dependency checking"""
        with self._lock:
            if name in self.modules:
                # Check if any other modules depend on this one
                dependent_modules = [
                    m.name for m in self.modules.values()
                    if m.dependencies and name in m.dependencies
                ]
                if dependent_modules:
                    raise ValueError(f"Cannot remove module {name}, required by: {dependent_modules}")
                
                del self.modules[name]
                self.logger.info(f"Unregistered module: {name}")

    def extend(self):
        """Execute modules in dependency order"""
        executed = set()
        
        def execute_module(name: str):
            if name in executed:
                return
                
            module = self.modules[name]
            
            # Execute dependencies first
            if module.dependencies:
                for dep in module.dependencies:
                    execute_module(dep)
            
            try:
                module.execute(self.context)
                executed.add(name)
            except Exception as e:
                self.logger.error(f"Error executing module {name}: {e}")
                raise

        # Execute all modules
        for name in self.modules:
            try:
                execute_module(name)
            except Exception as e:
                self.logger.error(f"Module execution failed: {e}")

    def cleanup(self):
        """Cleanup method to properly shutdown modularity"""
        with self._lock:
            # Execute cleanup in reverse dependency order
            for module in reversed(list(self.modules.values())):
                try:
                    if hasattr(module.execute, 'cleanup'):
                        module.execute.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up module {module.name}: {e}")
            
            self.modules.clear()
            self.context = ModuleContext()
