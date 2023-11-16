import os
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient
from docx import Document
import uuid
from src.app.settings import settings
from src.app.core.logs import logger


def extract_text_from_pdf(file_path):
    try:
        pdf = PdfReader(open(file_path, 'rb'))
        text = ''
        num_pages = len(pdf.pages)
        for page_num in range(num_pages):
            text += pdf.pages[page_num].extract_text()
        return text
    except Exception as e:
        print(f"An error occurred while reading PDF: {e}")
        return None


def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"An error occurred while reading TXT: {e}")
        return None


def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        print(f"An error occurred while reading DOCX: {e}")
        return None


def chunk_text(text, chunk_size=1000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def extract_text_from_file(file_path):
    """
    Extract text from the file.
    """
    print(file_path)
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return None


def extract_metadata(file_path):
    """
    Extract all possible metadata from the file,
    such as file name, size, extension, etc.
    """
    try:
        return {
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "file_extension": os.path.splitext(file_path)[1],
            "file_type": os.path.splitext(file_path)[1].replace(".", ""),
        }
    except Exception as e:
        print(f"An error occurred while extracting metadata: {e}")
        return {}


def populate_qdrant(client, documents, metadata, ids, settings):
    try:
        client.add(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            documents=documents,
            metadata=metadata,
            ids=ids,

        )
    except Exception as e:
        print(f"An error occurred while populating Qdrant: {e}")


def text_chunking_and_qdrant_upload(text: str, file_metadata: dict):
    """

    """

    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    logger.info(
        "Started Chunking text and extracting metadata from provided content.")

    documents = []
    metadata = []
    ids = []

    if text:
        chunks = chunk_text(text)

        for chunk in chunks:
            doc_id = str(uuid.uuid4())
            documents.append(chunk)
            metadata.append(
                {
                    "id": doc_id,
                    "chunk": chunk,
                    "chunk_length": len(chunk),
                    "file_name": file_metadata["file_name"],
                    "file_size": file_metadata["file_size"],
                    "file_extension": file_metadata["file_extension"],
                    "file_type": file_metadata["file_type"]
                }
            )
            ids.append(doc_id)
        logger.info(
            "Chunking text and extracting metadata from provided content was successful."
        )

    else:
        print("No text was provided.")
        logger.info("No text was provided.")

    if documents and metadata and ids:
        logger.info("Started populating Qdrant..")
        populate_qdrant(client, documents, metadata, ids, settings)
        logger.info("Qdrant was populated.")
    else:
        print("No documents, metadata, or ids were provided.")
        logger.info("No documents, metadata, or ids were provided.")


# if __name__ == "__main__":
#     client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

#     documents = []
#     metadata = []
#     ids = []

#     documents_directory = "./data"

#     file_to_id_mapping = {}

#     for file_name in os.listdir(documents_directory):
#         file_path = os.path.join(
#             documents_directory, file_name)

#         text = None

#         if file_name.endswith('.pdf'):
#             text = extract_text_from_pdf(file_path)
#         elif file_name.endswith('.txt'):
#             text = extract_text_from_txt(file_path)
#         elif file_name.endswith('.docx'):
#             text = extract_text_from_docx(file_path)

#         # extract metadata
#         file_metadata = extract_metadata(file_path)

#         # chunk the text into smaller chunks
#         if text:
#             chunks = chunk_text(text)

#             for chunk in chunks:
#                 doc_id = str(uuid.uuid4())
#                 file_to_id_mapping[file_name] = doc_id
#                 documents.append(chunk)
#                 metadata.append(
#                     {
#                         "source": file_name,
#                         "id": doc_id,
#                         "chunk": chunk,
#                         "chunk_length": len(chunk),
#                         "file_path": file_path,
#                         "file_metadata": file_metadata
#                     }
#                 )
#                 ids.append(doc_id)

#     # if documents and metadata and ids:
#     #     populate_qdrant(client, documents, metadata, ids, settings)
