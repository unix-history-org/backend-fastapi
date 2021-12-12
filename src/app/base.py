from fastapi import FastAPI

from src.app.api.admin.users import router as admin_user_router
from src.app.api.admin.os import router as admin_os_router
from src.app.api.os import router as os_router
from src.app.api.users import router as user_router
from src.app.api.emulation import router as emulation_router

from src.settings import settings
from src.app.core.db.connection import connect, disconnect


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(admin_os_router)
app.include_router(admin_user_router)
app.include_router(os_router)
app.include_router(user_router)
app.include_router(emulation_router)


@app.on_event('startup')
async def startup():
    await connect()


@app.on_event('shutdown')
async def shutdown():
    await disconnect()
