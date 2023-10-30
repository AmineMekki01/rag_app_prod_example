from fastapi import FastAPI 

from src.app.core.logs import logger
from src.app.core.api import router as core_router
from src.app import version


app = FastAPI(version=version)
app.include_router(core_router)
logger.info("Hey there!")

