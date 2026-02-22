from fastapi import FastAPI
from app.routes.generate import router as generate_router

app = FastAPI(title="Campus GenAI Studio")

app.include_router(generate_router)

@app.get("/")
def home():
    return {"message": "Campus GenAI Studio API running"}