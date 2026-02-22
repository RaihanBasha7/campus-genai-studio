import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router


# ── Logging Configuration ─────────────────────────────────────────────────────
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
})

logger = logging.getLogger(__name__)


# ── App Factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="Campus GenAI Studio – AI Engine",
        description=(
            "AI-powered event builder that converts raw campus ideas into fully "
            "structured, validated event plans using a local Ollama LLM."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],        # Lock down to specific origin in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(router)

    # ── Health Routes ─────────────────────────────────────────────────────────
    @app.get("/", tags=["Health"], summary="Root health check")
    def root():
        return {
            "status": "AI Engine Running",
            "service": "Campus GenAI Studio",
            "version": "1.0.0",
            "docs": "/docs"
        }

    @app.get("/health", tags=["Health"], summary="Detailed health status")
    def health():
        return {
            "status": "healthy",
            "ollama_model": "mistral:7b-instruct-q4_K_M",
            "ollama_url": "http://localhost:11434",
            "routes": ["/api/v1/generate-event"]
        }

    logger.info("Campus GenAI Studio AI Engine initialized.")
    return app


app = create_app()