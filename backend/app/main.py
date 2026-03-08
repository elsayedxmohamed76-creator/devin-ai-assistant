from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

app = FastAPI(
    title="Devin AI Assistant API",
    description="Neuro-symbolic learning AI assistant",
    version="1.0.0",
)

# CORS — restrict to local Electron app and dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:4173",   # Vite preview
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "app://.",                 # Electron custom protocol
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "engine": "neuro-symbolic", "version": "1.0.0"}
