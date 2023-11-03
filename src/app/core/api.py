from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException
from src.app.core.logs import logger

from starlette import status
from starlette.requests import Request
from qdrant_client import QdrantClient

from src.app.scripts.ingest import extract_text_from_pdf, extract_text_from_txt, extract_text_from_docx, populate_qdrant
from src.app.settings import settings

client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
router = APIRouter(tags=['Core Endpoints'])


@router.get('/healthCheck', status_code=status.HTTP_200_OK)
async def healthCheck(request: Request) -> dict:
    return {
        'Version': request.app.version
    }


@router.post("/v1/upload-document")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()
    file_location = f"data/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(contents)

    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(file_location)

    elif file.filename.endswith('.txt'):
        text = extract_text_from_txt(file_location)

    elif file.filename.endswith('.docx'):
        text = extract_text_from_docx(file_location)
    else:
        text = None

    if text is None:
        logger.error(
            f"File upload failed for {file.filename}, unsupported file type or content could not be extracted.")

        raise HTTPException(
            status_code=422, detail="Unsupported file type or content could not be extracted.")

    if text:
        populate_qdrant(client, [text], [file.filename], [
                        file.filename], settings)

    return {"text": text}


@router.get("/v1/documents")
async def read_documents():
    return {"documents": "List of documents"}
