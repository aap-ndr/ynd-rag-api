from fastapi import FastAPI
from pydantic import BaseModel

from rag import ask  # this comes from rag.py we created earlier

app = FastAPI(
    title="Youth Neurodiversity RAG Agent",
    description="A friendly AI Brain Buddy for neurodiversity education",
    version="1.0.0"
)

# ---------
# Schemas
# ---------
class Query(BaseModel):
    question: str


# ---------
# Routes
# ---------
@app.get("/")
def health_check():
    return {"status": "ok", "agent": "Spark"}

@app.post("/ask")
def ask_agent(query: Query):
    """
    Ask the neurodiversity RAG agent a question.
    """
    answer = ask(query.question)
    return {
        "answer": answer,
        "agent": "Spark"
    }
