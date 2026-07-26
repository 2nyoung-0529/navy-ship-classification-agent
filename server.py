from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from agent import WarshipAgent

app = FastAPI(
    title="Warship Agent API",
    description="대한민국 해군 함정 정보 조회 에이전트",
    version="1.0.0",
)

agent = WarshipAgent()


class HistoryItem(BaseModel):
    role: str
    content: str

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError("role은 'user' 또는 'assistant'여야 합니다.")
        return v


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryItem] | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message는 비어 있을 수 없습니다.")
        return v


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def root():
    return {"status": "ok", "service": "Warship Agent API"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        history = (
            [h.model_dump() for h in req.history] if req.history else None
        )
        reply = agent.chat(req.message, history)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy"}
