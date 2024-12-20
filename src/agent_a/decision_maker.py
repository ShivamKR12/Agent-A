import threading
import time
import queue
from typing import Callable, List, Dict, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import networkx as nx
from dataclasses import dataclass
from enum import Enum, auto

class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class Task:
    id: str
    callable: Callable
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    dependencies: List[str] = None
    priority: int = 0
    context: Dict[str, Any] = None

class DecisionContext:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any):
        with self._lock:
            self._data[key] = value

    def get(self, key: str, default=None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def update(self, data: Dict[str, Any]):
        with self._lock:
            self._data.update(data)

class DecisionMaker:
    def __init__(self, max_workers: int = 4, task_timeout: int = 60):
        self.logger = logging.getLogger(__name__)
        self.task_queue = queue.PriorityQueue()
        self.running = False
        self.reasoning_graph = nx.DiGraph()
        self.lock = threading.Lock()
        self.max_workers = max_workers
        self.task_timeout = task_timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}  # task_id -> Task
        self.context = DecisionContext()
        self._task_counter = 0

    def _get_next_task_id(self) -> str:
        with self.lock:
            self._task_counter += 1
            return f"task_{self._task_counter}"

    def add_task(self, task_callable: Callable, priority: int = 0, 
                 dependencies: List[str] = None, context: Dict[str, Any] = None) -> str:
        """Add a task with priority and dependencies"""
        if not callable(task_callable):
            raise ValueError("Task must be callable")

        task_id = self._get_next_task_id()
        task = Task(
            id=task_id,
            callable=task_callable,
            status=TaskStatus.PENDING,
            dependencies=dependencies or [],
            priority=priority,
            context=context or {}
        )

        try:
            self.task_queue.put((-priority, task))  # Negative priority for highest-first
            with self.lock:
                self.active_tasks[task_id] = task
            return task_id
        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            raise

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the current status of a task"""
        with self.lock:
            task = self.active_tasks.get(task_id)
            return task.status if task else None

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task"""
        with self.lock:
            task = self.active_tasks.get(task_id)
            if task and task.status == TaskStatus.COMPLETED:
                return task.result
            return None

    def _can_execute_task(self, task: Task) -> bool:
        """Check if all dependencies are completed"""
        if not task.dependencies:
            return True

        with self.lock:
            return all(
                self.active_tasks.get(dep_id) is not None and
                self.active_tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )

    def execute_tasks(self) -> None:
        """Main task execution loop"""
        self.running = True
        while self.running:
            try:
                _, task = self.task_queue.get(timeout=1)
                
                if not self._can_execute_task(task):
                    # Put back in queue with slightly lower priority
                    self.task_queue.put((-task.priority + 1, task))
                    continue

                self._safe_execute_task(task)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Task execution error: {e}")

    def _safe_execute_task(self, task: Task) -> None:
        """Execute a single task with proper context and error handling"""
        try:
            task.status = TaskStatus.RUNNING
            
            # Merge task context with global context
            execution_context = self.context._data.copy()
            execution_context.update(task.context)
            
            future = self.executor.submit(task.callable, execution_context)
            
            try:
                result = future.result(timeout=self.task_timeout)
                task.result = result
                task.status = TaskStatus.COMPLETED
                self.logger.debug(f"Task {task.id} completed successfully")
                
                # Update global context with task results if provided
                if isinstance(result, dict):
                    self.context.update(result)
                    
            except TimeoutError:
                self.logger.error(f"Task {task.id} timed out")
                task.status = TaskStatus.FAILED
                task.error = TimeoutError(f"Task timed out after {self.task_timeout} seconds")
                future.cancel()
            except Exception as e:
                self.logger.error(f"Task {task.id} failed: {e}")
                task.status = TaskStatus.FAILED
                task.error = e
                
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            task.status = TaskStatus.FAILED
            task.error = e

    def start(self) -> None:
        """Start the decision maker in a separate thread"""
        if not self.running:
            self.running = True
            threading.Thread(target=self.execute_tasks, daemon=True).start()
            self.logger.info("DecisionMaker started")

    def stop(self) -> None:
        """Stop the decision maker gracefully"""
        self.running = False
        
        # Cancel all pending tasks
        while not self.task_queue.empty():
            try:
                _, task = self.task_queue.get_nowait()
                task.status = TaskStatus.FAILED
                task.error = InterruptedError("DecisionMaker stopped")
            except queue.Empty:
                break
                
        # Shutdown executor
        self.executor.shutdown(wait=True)
        self.logger.info("DecisionMaker stopped")

    def create_reasoning_plan(self, query: str) -> List[str]:
        """Create a series of task IDs forming a reasoning plan"""
        steps = [
            {
                'name': 'analyze_query',
                'callable': self._analyze_query,
                'priority': 100
            },
            {
                'name': 'gather_context',
                'callable': self._gather_context,
                'priority': 90
            },
            {
                'name': 'generate_solution',
                'callable': self._generate_solution,
                'priority': 80
            },
            {
                'name': 'validate_solution',
                'callable': self._validate_solution,
                'priority': 70
            }
        ]

        task_ids = []
        prev_task_id = None

        for step in steps:
            task_id = self.add_task(
                step['callable'],
                priority=step['priority'],
                dependencies=[prev_task_id] if prev_task_id else None,
                context={'query': query}
            )
            task_ids.append(task_id)
            prev_task_id = task_id

        return task_ids

    # Example reasoning step implementations
    def _analyze_query(self, context: Dict[str, Any]) -> Dict[str, Any]:
        query = context.get('query', '')
        # Implement query analysis logic here
        return {'query_components': ['component1', 'component2']}

    def _gather_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implement context gathering logic here
        return {'additional_context': 'some_context'}

    def _generate_solution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implement solution generation logic here
        return {'solution': 'proposed_solution'}

    def _validate_solution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implement solution validation logic here
        return {'validation_result': True}
