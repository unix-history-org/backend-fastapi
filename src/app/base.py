from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.api.admin.users import router as admin_user_router
from app.api.admin.os import router as admin_os_router
from app.api.os import router as os_router
from app.api.users import router as user_router
from app.api.emulation import router as emulation_router

from settings import settings
from app.core.db.connection import connect, disconnect


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/doc/openapi.json",
    docs_url="/api/doc/docs",
    redoc_url="/api/doc/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_os_router)
app.include_router(admin_user_router)
app.include_router(os_router)
app.include_router(user_router)
app.include_router(emulation_router)


@app.get("/docs", response_class=RedirectResponse, include_in_schema=False)
async def doc():
    return "/api/doc/docs"


@app.on_event("startup")
async def startup():
    await connect()


@app.on_event("shutdown")
async def shutdown():
    await disconnect()
