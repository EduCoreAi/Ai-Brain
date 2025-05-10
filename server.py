# server.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from llama_cpp import Llama
import redis
import asyncio
import hashlib
import time

# Configuration
MODEL_PATH = "phi-3-mini-128k-instruct.Q4_K_M.gguf"  # Download from HuggingFace
API_PORT = 8000
REDIS_HOST = "localhost"

app = FastAPI()
cache = redis.Redis(host=REDIS_HOST, port=6379, db=0)

# AMD-optimized model loading
llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=20,           # Offload 20 layers to Radeon GPU
    n_threads=6,               # 6 physical cores
    n_ctx=8192,                # Context window
    n_batch=512,               # Match GPU VRAM
    offload_kqv=True,          # Reduce VRAM usage
    main_gpu=0,                # Single GPU
    use_mlock=True,            # Prevent swapping
    verbose=False
)

def get_cache_key(prompt: str) -> str:
    return f"cache:{hashlib.sha256(prompt.encode()).hexdigest()}"

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    prompt = data["prompt"].strip()
    
    # Cache check
    if cached := cache.get(get_cache_key(prompt)):
        return {"response": cached.decode()}
    
    # Stream response
    async def generate():
        full_response = []
        stream = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )
        
        for chunk in stream:
            content = chunk["choices"][0]["delta"].get("content", "")
            full_response.append(content)
            yield f"data: {content}\n\n"
            await asyncio.sleep(0.001)
        
        # Cache response for 1 hour
        final_response = "".join(full_response)
        cache.setex(get_cache_key(prompt), 3600, final_response)

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=API_PORT,
        workers=2,              # 2 processes for 6-core CPU
        loop="uvloop",
        http="httptools"
    )
