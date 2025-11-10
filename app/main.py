import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router
from app.routers.session import router as session_router
from app.core.config import settings

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins={settings.ALLOWED_ORIGINS},
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(chat_router)
app.include_router(session_router)

if __name__ == "__main__":

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )


@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} API is running",
        "status": "healthy",
        "debug_mode": settings.DEBUG
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}