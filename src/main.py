import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
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