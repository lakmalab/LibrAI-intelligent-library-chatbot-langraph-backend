import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.v1.chat import router as chat_router
from src.routers.v1.session import router as session_router
from src.routers.v1.chat import ChatController
from src.utils.config import settings

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
        "src.main:app",
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