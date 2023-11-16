from qdrant_client import QdrantClient

from src.app.chat.exceptions import RetrievalNoDocumentsFoundException
from src.app.chat.models import BaseMessage
from src.app.core.logs import logger
from src.app.settings import settings


client = QdrantClient(settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def process_retrieval(message: BaseMessage) -> BaseMessage:
    """ Search for a given query using vector similarity search. If no documents are found we raise an exception.
    If we do find documents we take the top 3 and put them into the context."""
    search_result = search(query=message.message)
    resulting_query: str = (
        f"Answer based only on the context, nothing else. \n"
        f"QUERY:\n{message.message}\n"
        f"CONTEXT:\n{search_result}"
    )

    return BaseMessage(message=resulting_query, model=message.model)


def search(query: str) -> str:
    """ Search for a given query using vector similarity search. If no documents are found we raise an exception. """
    search_result = client.query(
        collection_name=settings.QDRANT_COLLECTION_NAME, query_text=query)

    if not search_result:
        raise RetrievalNoDocumentsFoundException

    # Joining the 'document' content from each result
    return "\n".join(result.document for result in search_result)
