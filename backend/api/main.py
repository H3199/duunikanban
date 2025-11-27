from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.jobs import router as jobs_router
from core.database import init_db


app = FastAPI(title="Duunikanban API")


@app.on_event("startup")
def on_startup():
    init_db()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(jobs_router, prefix="/api/v1")
