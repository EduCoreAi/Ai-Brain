from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import requests
import tempfile
from typing import Optional
from .database import init_db, log_feedback, log_document, get_feedback, get_documents
from fastapi.middleware.cors import CORSMiddleware
import openai
from anthropic import Anthropic
import tiktoken

# Initialize database
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "API_URL = ""http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
openai.api_key = OPENAI_API_KEY
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

class ChatRequest(BaseModel):
    prompt: str
    model: str = "llama3"
    use_cloud: bool = False

class IngestRequest(BaseModel):
    domain: str = "general"

class FeedbackRequest(BaseModel):
    prompt: str
    response: str
    rating: int
    correction: str = ""

# --- Core Endpoints ---
@app.get("/health")
async def health():
    return {"status": "OK"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        if req.use_cloud:
            return await handle_cloud_chat(req.prompt)
        else:
            return await handle_local_chat(req.prompt, req.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_local_chat(prompt: str, model: str):
    ollama_url = f"{OLLAMA_ENDPOINT}/api/generate"
    response = requests.post(ollama_url, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    }, timeout=120)
    response.raise_for_status()
    return {"response": response.json().get("response", "[No response]")}

async def handle_cloud_chat(prompt: str):
    try:  # Try OpenAI first
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response.choices[0].message.content}
    except:  # Fallback to Claude
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response.content[0].text}

@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...), domain: str = "general"):
    try:
        contents = await file.read()
        text = contents.decode('utf-8')
        
        # Save to disk
        os.makedirs("data/ingested", exist_ok=True)
        file_path = f"data/ingested/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Save to DB
        log_document(file.filename, text, domain)
        
        return {"status": "ingested", "path": file_path}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/feedback")
async def feedback(req: FeedbackRequest):
    log_feedback(req.prompt, req.response, req.rating, req.correction)
    return {"status": "logged"}

@app.get("/feedback")
async def get_feedback_endpoint(limit: int = 100):
    return get_feedback()[:limit]

@app.get("/documents")
async def get_documents_endpoint(domain: Optional[str] = None):
    return get_documents(domain)
