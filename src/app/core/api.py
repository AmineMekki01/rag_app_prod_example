from fastapi import APIRouter

from starlette import status 
from starlette.requests import Request

router = APIRouter(tags = ['Core Endpoints'])

@router.get('/healthCheck', status_code=status.HTTP_200_OK)	
async def healthCheck(request : Request) -> dict:
    return {
        'Version' : 'request.app.version'
    }