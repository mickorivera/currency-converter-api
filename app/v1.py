from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.api import router


app = FastAPI(
    title="Currencies API",
    version = "v1",
    docs_url="/v1",
    openapi_url="/v1/openapi.json",
    description="Currency rate conversion API",
)
app.include_router(router, prefix="/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
