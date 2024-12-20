from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import threading
import asyncio

class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None

class APIServer:
    def __init__(self, agent: 'AgentA'):
        self.agent = agent
        self.app = FastAPI(title="Agent-A API")
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/command", response_model=CommandResponse)
        async def execute_command(request: CommandRequest):
            try:
                # Create task context
                context = request.context or {}
                context.update({
                    "source": "api",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Create task
                task = Task(
                    id=f"api_{uuid4().hex[:8]}",
                    callable=self.agent._process_command,
                    priority=TaskPriority.MEDIUM,
                    context={"command": request.command, **context},
                    timeout=30
                )
                
                # Execute task and wait for result
                future = self.agent.decision_maker.executor.submit(
                    self.agent._process_command,
                    task.context
                )
                
                result = future.result(timeout=30)
                
                return CommandResponse(
                    success=True,
                    result=result
                )
                
            except Exception as e:
                return CommandResponse(
                    success=False,
                    error=str(e)
                )

        @self.app.get("/status")
        async def get_status():
            return {
                "running": self.agent.running,
                "tasks_active": len(self.agent.decision_maker.active_tasks),
                "modules_loaded": len(self.agent.modularity.modules)
            }

    def start(self):
        """Start the API server in a separate thread"""
        def run_server():
            uvicorn.run(
                self.app,
                host=self.agent.config.api_host,
                port=self.agent.config.api_port
            )

        threading.Thread(target=run_server, daemon=True).start()
