from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import WarshipAgent

app = FastAPI(
    title="Warship Agent API",
    description="대한민국 해군 현역 함정 정보 조회 에이전트",
    version="1.0.0",
)

agent = WarshipAgent()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def root():
    return {"status": "ok", "service": "Warship Agent API"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        reply = agent.chat(req.message, req.history)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy"}
