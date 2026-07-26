"""
FastAPI bridge for the AI Operations Copilot.

Exposes:
  GET  /health  — connectivity + agent mode for the UI status badge
  POST /ask     — { "question": "..." } → { "answer": "..." }
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.copilot import ask_copilot, get_agent_mode

app = FastAPI(
    title="AI Operations Copilot",
    description="Agentic industrial asset monitoring API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Natural-language question about plant assets")


class AskResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str
    mode: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", mode=get_agent_mode())


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        answer = ask_copilot(question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Copilot failed: {exc}") from exc
    return AskResponse(answer=answer)
