import os
import asyncio
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import structlog

from agents.educational_router import EducationalRouterAgent
from agents.realtime_grid_agent import RealtimeGridAgent
from models.database import init_db, ApiUsage, AsyncSessionLocal
from sqlalchemy import select, func

logger = structlog.get_logger()

app = FastAPI(
    title="Sentient Playground Agent Service",
    description="Educational GRID workflow orchestration backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

active_connections: dict[str, WebSocket] = {}
jobs: dict[str, dict] = {}


class AskRequest(BaseModel):
    prompt: str
    lessonId: Optional[str] = None
    userId: Optional[str] = None


class AskResponse(BaseModel):
    jobId: str
    wsUrl: str


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Sentient Playground Agent Service")
    await init_db()


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/settings.html")
async def settings():
    return FileResponse("static/settings.html")


@app.get("/demo.html")
async def demo():
    return FileResponse("static/demo.html")


@app.get("/health")
async def health_check():
    # Check if real-time mode is available
    realtime_agent = RealtimeGridAgent()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "realtimeAvailable": realtime_agent.is_available()
    }


@app.get("/api/usage/{user_id}")
async def get_usage_stats(user_id: str):
    """Get API usage statistics for a user"""
    try:
        async with AsyncSessionLocal() as session:
            # Total usage
            total_query = select(
                func.count(ApiUsage.id).label('total_calls'),
                func.sum(ApiUsage.tokens_used).label('total_tokens'),
                func.sum(ApiUsage.estimated_cost).label('total_cost')
            ).where(ApiUsage.user_id == user_id)
            
            result = await session.execute(total_query)
            total_stats = result.one()
            
            # Provider breakdown
            provider_query = select(
                ApiUsage.provider,
                func.count(ApiUsage.id).label('calls'),
                func.sum(ApiUsage.tokens_used).label('tokens'),
                func.sum(ApiUsage.estimated_cost).label('cost')
            ).where(ApiUsage.user_id == user_id).group_by(ApiUsage.provider)
            
            provider_result = await session.execute(provider_query)
            provider_stats = provider_result.all()
            
            return {
                "userId": user_id,
                "totalCalls": total_stats.total_calls or 0,
                "totalTokens": total_stats.total_tokens or 0,
                "totalCost": float(total_stats.total_cost or 0),
                "providers": [
                    {
                        "provider": p.provider,
                        "calls": p.calls,
                        "tokens": p.tokens,
                        "cost": float(p.cost)
                    } for p in provider_stats
                ]
            }
    except Exception as e:
        logger.error("Failed to fetch usage stats", error=str(e))
        return {
            "userId": user_id,
            "totalCalls": 0,
            "totalTokens": 0,
            "totalCost": 0.0,
            "providers": []
        }


@app.post("/api/ask", response_model=AskResponse)
async def create_job(
    request: AskRequest,
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_anthropic_key: Optional[str] = Header(None, alias="X-Anthropic-Key"),
    x_fireworks_key: Optional[str] = Header(None, alias="X-Fireworks-Key"),
    x_dobby_model: Optional[str] = Header(None, alias="X-Dobby-Model")
):
    job_id = str(uuid.uuid4())
    
    # Check if real-time mode is available with user-provided keys
    realtime_agent = RealtimeGridAgent(
        openai_key=x_openai_key,
        anthropic_key=x_anthropic_key,
        fireworks_key=x_fireworks_key,
        dobby_model=x_dobby_model
    )
    use_realtime = realtime_agent.is_available()
    
    # Store job metadata WITHOUT API keys (keys are session-scoped only)
    jobs[job_id] = {
        "id": job_id,
        "prompt": request.prompt,
        "lessonId": request.lessonId,
        "userId": request.userId,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "realtime": use_realtime
    }
    
    # Store API keys temporarily in-memory for WebSocket connection only
    # Keys will be deleted immediately after WebSocket establishes
    active_connections[f"{job_id}_keys"] = {
        "openai": x_openai_key,
        "anthropic": x_anthropic_key,
        "fireworks": x_fireworks_key,
        "dobby_model": x_dobby_model
    }
    
    logger.info("Created job", job_id=job_id, prompt=request.prompt[:100], realtime=use_realtime)
    
    ws_base = os.getenv("WS_BASE", "ws://localhost:8000")
    
    return AskResponse(
        jobId=job_id,
        wsUrl=f"{ws_base}/ws/stream?jobId={job_id}"
    )


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket, jobId: str):
    await websocket.accept()
    active_connections[jobId] = websocket
    
    logger.info("WebSocket connected", job_id=jobId)
    
    try:
        if jobId not in jobs:
            await websocket.send_json({
                "type": "ERROR",
                "jobId": jobId,
                "ts": datetime.utcnow().isoformat(),
                "detail": "Job not found"
            })
            await websocket.close()
            return
        
        job = jobs[jobId]
        prompt = job["prompt"]
        use_realtime = job.get("realtime", False)
        user_id = job.get("userId") or "local"  # Use "local" if userId is None or empty
        
        # Retrieve API keys from temporary storage (request-scoped)
        api_keys_key = f"{jobId}_keys"
        api_keys = active_connections.get(api_keys_key, {})
        
        # IMMEDIATELY delete API keys from memory after retrieval
        if api_keys_key in active_connections:
            del active_connections[api_keys_key]
        
        # Use real-time agent if API keys are available, otherwise use educational demo
        if use_realtime:
            agent = RealtimeGridAgent(
                openai_key=api_keys.get("openai"),
                anthropic_key=api_keys.get("anthropic"),
                fireworks_key=api_keys.get("fireworks"),
                dobby_model=api_keys.get("dobby_model")
            )
        else:
            agent = EducationalRouterAgent()
        
        async for event in agent.process(prompt, jobId, user_id):
            await websocket.send_json(event)
        
        await websocket.send_json({
            "type": "COMPLETE",
            "jobId": jobId,
            "ts": datetime.utcnow().isoformat()
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", job_id=jobId)
    except Exception as e:
        logger.error("WebSocket error", job_id=jobId, error=str(e))
        try:
            await websocket.send_json({
                "type": "ERROR",
                "jobId": jobId,
                "ts": datetime.utcnow().isoformat(),
                "detail": str(e)
            })
        except:
            pass
    finally:
        if jobId in active_connections:
            del active_connections[jobId]


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
