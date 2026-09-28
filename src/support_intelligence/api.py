from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from support_intelligence.db import Base, engine, save_message
from support_intelligence.messages import normalize_message
from support_intelligence.retrieval import add_document, search_documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables when the application starts."""
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="AI Support Intelligence Platform", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    id: int
    message: str
    intent: str
    answer: str
    sources: list[str]


class DocumentRequest(BaseModel):
    text: str
    source: str


def clean_text(text: str) -> str:
    """Normalize input and return an HTTP 422 error when it is empty."""
    try:
        return normalize_message(text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def classify_intent(message: str) -> str:
    """Assign a temporary rule-based intent to a customer message."""
    lowered = message.lower()

    if "order" in lowered or "tracking" in lowered:
        return "order_status"
    if "refund" in lowered or "return" in lowered:
        return "refund"
    return "general_question"


@app.get("/health")
def health() -> dict[str, str]:
    """Report whether the API process is running."""
    return {"status": "ok"}


@app.post("/documents")
def create_document(request: DocumentRequest) -> dict[str, str]:
    """Validate a support document and store it in Qdrant."""
    text = clean_text(request.text)
    source = clean_text(request.source)
    return {"id": add_document(text, source)}


@app.get("/search")
def search(q: str) -> dict[str, list[dict]]:
    """Retrieve documents related to the search query."""
    return {"results": search_documents(clean_text(q))}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Save a message and answer from the best matching support document."""
    message = clean_text(request.message)
    intent = classify_intent(message)
    saved = save_message(message, intent)

    matches = search_documents(message)
    useful_matches = [item for item in matches if item["score"] >= 0.25]

    if useful_matches:
        best = useful_matches[0]
        answer = best["text"]
        sources = [best["source"]]
    else:
        answer = "I could not find a reliable answer in the support documents."
        sources = []

    return ChatResponse(
        id=saved.id,
        message=message,
        intent=intent,
        answer=answer,
        sources=sources,
    )