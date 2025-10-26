import os
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional
import structlog
from litellm import acompletion
from models.database import ApiUsage, AsyncSessionLocal

logger = structlog.get_logger()


class RealtimeGridAgent:
    """
    Real-time GRID agent using actual LLM providers.
    Demonstrates authentic multi-agent workflow with streaming responses.
    """
    
    def __init__(self, openai_key: Optional[str] = None, anthropic_key: Optional[str] = None, fireworks_key: Optional[str] = None, dobby_model: Optional[str] = None):
        self.logger = logger.bind(agent="RealtimeGrid")
        
        # Accept keys from parameters or environment (never mutate os.environ)
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
        self.fireworks_key = fireworks_key or os.getenv("FIREWORKS_API_KEY")
        self.dobby_model = dobby_model
        
        # Choose best available model (keys remain request-scoped, never stored in environment)
        if self.fireworks_key and self.dobby_model:
            # Use Dobby if Fireworks key is provided
            self.router_model = dobby_model
            self.worker_model = dobby_model
        elif self.anthropic_key:
            self.router_model = "claude-3-5-sonnet-20241022"
            self.worker_model = "claude-3-5-haiku-20241022"
        elif self.openai_key:
            self.router_model = "gpt-4o"
            self.worker_model = "gpt-4o-mini"
        else:
            self.router_model = None
            self.worker_model = None
    
    def is_available(self) -> bool:
        """Check if real-time mode is available"""
        return self.router_model is not None
    
    async def _track_usage(self, model: str, response: Any, job_id: str, user_id: str = "local"):
        """Track API usage in database with cost estimation"""
        try:
            # Extract token usage
            usage = response.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
            
            # Estimate cost based on model (prices per 1M tokens)
            cost = 0.0
            provider = "unknown"
            
            if "gpt-4o" in model:
                provider = "openai"
                # GPT-4o: $2.50 input, $10 output per 1M tokens
                cost = (prompt_tokens * 2.50 / 1_000_000) + (completion_tokens * 10.0 / 1_000_000)
            elif "gpt-4o-mini" in model:
                provider = "openai"
                # GPT-4o-mini: $0.15 input, $0.60 output per 1M tokens
                cost = (prompt_tokens * 0.15 / 1_000_000) + (completion_tokens * 0.60 / 1_000_000)
            elif "claude-3-5-sonnet" in model:
                provider = "anthropic"
                # Claude 3.5 Sonnet: $3 input, $15 output per 1M tokens
                cost = (prompt_tokens * 3.0 / 1_000_000) + (completion_tokens * 15.0 / 1_000_000)
            elif "claude-3-5-haiku" in model:
                provider = "anthropic"
                # Claude 3.5 Haiku: $0.80 input, $4 output per 1M tokens
                cost = (prompt_tokens * 0.80 / 1_000_000) + (completion_tokens * 4.0 / 1_000_000)
            elif "dobby" in model.lower():
                provider = "fireworks"
                # Fireworks Dobby: Estimate $1 input, $1 output per 1M tokens
                cost = (prompt_tokens * 1.0 / 1_000_000) + (completion_tokens * 1.0 / 1_000_000)
            
            # Save to database
            async with AsyncSessionLocal() as session:
                usage_record = ApiUsage(
                    user_id=user_id,
                    job_id=job_id,
                    provider=provider,
                    model=model,
                    tokens_used=total_tokens,
                    estimated_cost=cost
                )
                session.add(usage_record)
                await session.commit()
                
            self.logger.info("Usage tracked", model=model, tokens=total_tokens, cost=cost)
        except Exception as e:
            self.logger.error("Failed to track usage", error=str(e))
    
    def _get_api_key_for_model(self, model: str) -> Optional[str]:
        """Get the appropriate API key for a given model (request-scoped)"""
        if self.dobby_model and self.dobby_model in model:
            return self.fireworks_key
        elif "claude" in model:
            return self.anthropic_key
        elif "gpt" in model:
            return self.openai_key
        return None
    
    async def process(self, prompt: str, job_id: str, user_id: str = "local") -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a user prompt through real GRID workflow with actual LLM calls.
        Emits events at each stage with real-time responses.
        """
        self.logger.info("Starting real-time GRID workflow", job_id=job_id, user_id=user_id, prompt=prompt[:100])
        
        if not self.is_available():
            yield {
                "type": "ERROR",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "detail": "No API keys configured. Please add OPENAI_API_KEY or ANTHROPIC_API_KEY."
            }
            return
        
        # Stage 1: Route to GRID
        yield {
            "type": "ROUTED",
            "jobId": job_id,
            "ts": datetime.utcnow().isoformat(),
            "nodeId": "user",
            "nodeLabel": "User Query",
            "detail": f"Query routed to GRID using {self.router_model}"
        }
        await asyncio.sleep(0.3)
        
        # Stage 2: Classification with real LLM
        workflow_type, classification_reasoning = await self._classify_query_llm(prompt, job_id, user_id)
        yield {
            "type": "CLASSIFIED",
            "jobId": job_id,
            "ts": datetime.utcnow().isoformat(),
            "nodeId": "router",
            "nodeLabel": "GRID Router",
            "detail": f"Classified as '{workflow_type}' - {classification_reasoning}"
        }
        await asyncio.sleep(0.5)
        
        # Stage 3: Workflow Planning with LLM
        tasks = await self._plan_workflow_llm(prompt, workflow_type, job_id, user_id)
        yield {
            "type": "WORKFLOW_PLANNED",
            "jobId": job_id,
            "ts": datetime.utcnow().isoformat(),
            "nodeId": "planner",
            "nodeLabel": "Workflow Planner",
            "detail": f"Decomposed into {len(tasks)} specialized tasks"
        }
        await asyncio.sleep(0.5)
        
        # Stage 4: Execute tasks with specialized agents
        task_results = []
        for i, task in enumerate(tasks):
            yield {
                "type": "TASK_ASSIGNED",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": f"agent_{i}",
                "nodeLabel": task["agent"],
                "detail": f"Assigned to {task['agent']}: {task['description']}"
            }
            await asyncio.sleep(0.3)
            
            # Execute task with real LLM
            task_result = None
            async for update in self._execute_task_llm(task, prompt, job_id, i, user_id):
                if update.get("result"):
                    task_result = update["result"]
                yield update
            
            # Store result for composition
            task["result"] = task_result or f"Completed {task['description']}"
            task_results.append(task)
            
            yield {
                "type": "TASK_DONE",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": f"agent_{i}",
                "nodeLabel": task["agent"],
                "detail": f"{task['agent']} completed successfully"
            }
            await asyncio.sleep(0.3)
        
        # Stage 5: Composition with streaming
        yield {
            "type": "COMPOSE_START",
            "jobId": job_id,
            "ts": datetime.utcnow().isoformat(),
            "nodeId": "composer",
            "nodeLabel": "Result Composer",
            "detail": "Synthesizing results from all agents..."
        }
        await asyncio.sleep(0.5)
        
        # Generate final answer with streaming
        async for chunk in self._compose_answer_streaming(prompt, task_results, job_id, user_id):
            yield chunk
        
        yield {
            "type": "COMPOSE_DONE",
            "jobId": job_id,
            "ts": datetime.utcnow().isoformat(),
            "nodeId": "composer",
            "nodeLabel": "Result Composer",
            "detail": "Final answer complete"
        }
        
        self.logger.info("Real-time GRID workflow completed", job_id=job_id)
    
    async def _classify_query_llm(self, prompt: str, job_id: str = "", user_id: str = "local") -> tuple[str, str]:
        """Classify the query using real LLM"""
        try:
            response = await acompletion(
                model=self.router_model,
                api_key=self._get_api_key_for_model(self.router_model),
                messages=[{
                    "role": "system",
                    "content": "You are a query classifier for the Sentient GRID. Classify the user's query into ONE category: explanation, summarization, research, code_generation, or general_query. Respond with JSON: {\"category\": \"...\", \"reasoning\": \"brief explanation\"}"
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3,
                max_tokens=150
            )
            
            # Track usage
            await self._track_usage(self.router_model, response, job_id, user_id)
            
            content = response.choices[0].message.content
            # Simple JSON extraction
            if "explanation" in content.lower():
                return "explanation", "Query seeks to understand a concept"
            elif "summarization" in content.lower():
                return "summarization", "Query requests a summary"
            elif "research" in content.lower():
                return "research", "Query requires information gathering"
            elif "code" in content.lower():
                return "code_generation", "Query involves coding"
            else:
                return "general_query", "General information request"
                
        except Exception as e:
            self.logger.error("LLM classification failed", error=str(e))
            return "general_query", "Fallback classification"
    
    async def _plan_workflow_llm(self, prompt: str, workflow_type: str, job_id: str = "", user_id: str = "local") -> list[Dict[str, str]]:
        """Plan workflow tasks using LLM"""
        try:
            response = await acompletion(
                model=self.router_model,
                api_key=self._get_api_key_for_model(self.router_model),
                messages=[{
                    "role": "system",
                    "content": "You are a workflow planner for the Sentient GRID. Break down the user's query into 2-4 specific subtasks that different specialized agents should handle. Each task should have an agent type and description."
                }, {
                    "role": "user",
                    "content": f"Query type: {workflow_type}\nQuery: {prompt}\n\nProvide 2-4 subtasks as a simple list, one per line, format: 'AgentName: description'"
                }],
                temperature=0.5,
                max_tokens=300
            )
            
            # Track usage
            await self._track_usage(self.router_model, response, job_id, user_id)
            
            content = response.choices[0].message.content
            lines = [line.strip() for line in content.split('\n') if ':' in line and line.strip()]
            
            tasks = []
            for line in lines[:4]:  # Max 4 tasks
                if ':' in line:
                    agent, desc = line.split(':', 1)
                    # Clean up markdown/numbering
                    agent = agent.strip('- ').strip('123456789. ')
                    tasks.append({
                        "agent": agent.strip(),
                        "description": desc.strip()
                    })
            
            # Fallback if parsing failed
            if not tasks:
                tasks = [
                    {"agent": "Research Agent", "description": "Gather relevant information"},
                    {"agent": "Analysis Agent", "description": "Process and analyze data"},
                    {"agent": "Synthesis Agent", "description": "Formulate comprehensive answer"}
                ]
            
            return tasks
            
        except Exception as e:
            self.logger.error("LLM planning failed", error=str(e))
            return [
                {"agent": "Research Agent", "description": "Information gathering"},
                {"agent": "Processing Agent", "description": "Data analysis"}
            ]
    
    async def _execute_task_llm(self, task: Dict[str, str], prompt: str, job_id: str, agent_id: int, user_id: str = "local") -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a single task using real LLM calls"""
        try:
            # Emit start update
            yield {
                "type": "TASK_UPDATE",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": f"agent_{agent_id}",
                "nodeLabel": task["agent"],
                "detail": f"{task['agent']}: Processing with {self.worker_model}...",
                "progress": 30
            }
            
            # Execute the task with real LLM
            response = await acompletion(
                model=self.worker_model,
                api_key=self._get_api_key_for_model(self.worker_model),
                messages=[{
                    "role": "system",
                    "content": f"You are the {task['agent']} in a multi-agent system. Your specific role: {task['description']}. Provide a focused, concise result for your assigned subtask."
                }, {
                    "role": "user",
                    "content": f"Original user query: {prompt}\n\nYour subtask: {task['description']}\n\nProvide your specialized result."
                }],
                temperature=0.7,
                max_tokens=400
            )
            
            # Track usage
            await self._track_usage(self.worker_model, response, job_id, user_id)
            
            result = response.choices[0].message.content
            
            # Emit completion
            yield {
                "type": "TASK_UPDATE",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": f"agent_{agent_id}",
                "nodeLabel": task["agent"],
                "detail": f"{task['agent']}: Complete",
                "progress": 100,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed for {task['agent']}", error=str(e))
            # Fallback result
            yield {
                "type": "TASK_UPDATE",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": f"agent_{agent_id}",
                "nodeLabel": task["agent"],
                "detail": f"{task['agent']}: Completed (fallback)",
                "progress": 100,
                "result": f"Processed: {task['description']}"
            }
    
    async def _compose_answer_streaming(self, prompt: str, tasks: list[Dict[str, str]], job_id: str, user_id: str = "local") -> AsyncGenerator[Dict[str, Any], None]:
        """Generate final answer with streaming"""
        try:
            # Build summary with actual results from agents
            task_summary = "\n".join([
                f"- {t['agent']}: {t.get('result', t['description'])}" 
                for t in tasks
            ])
            
            response = await acompletion(
                model=self.router_model,
                api_key=self._get_api_key_for_model(self.router_model),
                messages=[{
                    "role": "system",
                    "content": "You are the final synthesis agent in the Sentient GRID. Compose a comprehensive, helpful answer based on the workflow that was executed. Be informative and educational."
                }, {
                    "role": "user",
                    "content": f"User asked: {prompt}\n\nOur multi-agent workflow executed:\n{task_summary}\n\nProvide a clear, comprehensive answer to the user's question."
                }],
                temperature=0.7,
                max_tokens=800,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            full_text = ""
            final_chunk = None
            async for chunk in response:
                final_chunk = chunk
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_text += content
                    
                    yield {
                        "type": "FINAL",
                        "jobId": job_id,
                        "ts": datetime.utcnow().isoformat(),
                        "nodeId": "final",
                        "nodeLabel": "Final Answer",
                        "partialText": content,
                        "fullText": full_text,
                        "streaming": True
                    }
                    await asyncio.sleep(0.01)
            
            # Track usage if available (streaming responses may include usage in final chunk)
            if final_chunk and hasattr(final_chunk, 'usage') and final_chunk.usage:
                # Create a mock response object for tracking
                mock_response = {
                    'usage': {
                        'prompt_tokens': final_chunk.usage.prompt_tokens if hasattr(final_chunk.usage, 'prompt_tokens') else 0,
                        'completion_tokens': final_chunk.usage.completion_tokens if hasattr(final_chunk.usage, 'completion_tokens') else 0,
                        'total_tokens': final_chunk.usage.total_tokens if hasattr(final_chunk.usage, 'total_tokens') else 0
                    }
                }
                await self._track_usage(self.router_model, mock_response, job_id, user_id)
            
            # Send completion marker
            yield {
                "type": "FINAL",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": "final",
                "nodeLabel": "Final Answer",
                "detail": full_text,
                "fullText": full_text,
                "streaming": False,
                "complete": True
            }
            
        except Exception as e:
            self.logger.error("LLM composition failed", error=str(e))
            fallback_answer = (
                f"I've processed your query '{prompt}' through our multi-agent GRID workflow. "
                f"The workflow involved {len(tasks)} specialized agents working together. "
                "While I encountered an issue generating the detailed response, the demonstration "
                "shows how the Sentient GRID routes queries through specialized agents for optimal results."
            )
            yield {
                "type": "FINAL",
                "jobId": job_id,
                "ts": datetime.utcnow().isoformat(),
                "nodeId": "final",
                "nodeLabel": "Final Answer",
                "detail": fallback_answer,
                "fullText": fallback_answer,
                "complete": True
            }
