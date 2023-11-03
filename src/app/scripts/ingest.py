import os
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient
from docx import Document
import uuid
from src.app.settings import settings


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
        with open(file_path, 'r') as f:
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


def populate_qdrant(client, documents, metadata, ids, settings):
    try:
        client.add(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            documents=documents,
            metadata=metadata,
            ids=ids
        )
    except Exception as e:
        print(f"An error occurred while populating Qdrant: {e}")


if __name__ == "__main__":
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    documents = []
    metadata = []
    ids = []

    documents_directory = "./data"

    file_to_id_mapping = {}

    for file_name in os.listdir(documents_directory):
        file_path = os.path.join(
            documents_directory, file_name)

        text = None

        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_name.endswith('.txt'):
            text = extract_text_from_txt(file_path)
        elif file_name.endswith('.docx'):
            text = extract_text_from_docx(file_path)

        if text:
            doc_id = str(uuid.uuid4())
            file_to_id_mapping[file_name] = doc_id
            documents.append(text)
            metadata.append({"source": file_name})
            ids.append(doc_id)

    if documents and metadata and ids:
        populate_qdrant(client, documents, metadata, ids, settings)
