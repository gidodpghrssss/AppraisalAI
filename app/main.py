from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_stack import LlamaStack
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.health import router as health_router

app = FastAPI(
    title="AI Appraisal System",
    description="Advanced AI-powered real estate appraisal system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Llama Stack
llama_stack = LlamaStack(
    api_key=settings.LLAMA_API_KEY,
    api_url=settings.LLAMA_API_URL
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(health_router, prefix="/health")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Appraisal System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
