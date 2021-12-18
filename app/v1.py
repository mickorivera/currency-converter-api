from fastapi import FastAPI, status

from app.endpoints.api import router


app = FastAPI(
    title="Currencies API",
    version = "v1",
    docs_url="/v1",
    openapi_url="/v1/openapi.json",
    description="Currency rate conversion API",
)
app.include_router(router, prefix="/v1")
