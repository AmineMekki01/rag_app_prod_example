from fastapi import APIRouter

import openai
from starlette.responses import StreamingResponse

from src.app.chat.exceptions import OpenAIException
from src.app.chat.models import BaseMessage, Message
from src.app.chat.services import OpenAIService
from src.app.db import messages_queries


router = APIRouter(tags=["Chat Endpoints"])


@router.get("/v1/messages")
async def get_messages() -> list[Message]:
    # a bit messy as we might want to move this to a service
    return [Message(**message) for message in messages_queries.select_all()]


@router.post("/v1/completion")
async def completion_create(input_message: BaseMessage) -> Message:
    try:
        answer = await OpenAIService.chat_completion_without_streaming(input_message=input_message)

        # Insert the message into the database
        messages_queries.insert(
            model=input_message.model,
            role=answer.role,
            message=input_message.message,
            answer=answer.message
        )

        return answer
    except openai.OpenAIError:
        raise OpenAIException


@router.post("/v1/completion-stream")
async def completion_stream(input_message: BaseMessage) -> StreamingResponse:
    """Streaming response won't return json but rather a properly formatted string for SSE."""
    try:
        return await OpenAIService.chat_completion_with_streaming(input_message=input_message)
    except openai.OpenAIError:
        raise OpenAIException


@router.post("/v1/qa-create")
async def qa_create(input_message: BaseMessage) -> Message:
    try:
        return await OpenAIService.qa_without_stream(input_message=input_message)
    except openai.OpenAIError:
        raise OpenAIException


@router.post("/v1/qa-stream")
async def qa_stream(input_message: BaseMessage) -> StreamingResponse:
    """Streaming response won't return json but rather a properly formatted string for SSE."""
    try:
        return await OpenAIService.qa_with_stream(input_message=input_message)
    except openai.OpenAIError:
        raise OpenAIException
