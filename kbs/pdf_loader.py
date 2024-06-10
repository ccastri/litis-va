from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Query,
    APIRouter,
    Depends,
    status,
)
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.redis import Redis
from dotenv import load_dotenv
import os
import tempfile
import redis
from typing import List, Dict, Union
import json


load_dotenv()
router = APIRouter()
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")

# Create a Redis connection
redis_url = f"redis://default:{redis_password}@{redis_host}:{redis_port}"
redis_client = redis.StrictRedis.from_url(redis_url)


@router.post("/process-file")
async def process_file(file: UploadFile = File(...)):
    try:
        if file.content_type == "text/plain":
            Loader = TextLoader
        elif file.content_type == "application/pdf":
            Loader = PyPDFLoader
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        # Specify a custom temporary directory (change to your preferred directory)
        #! Cambiar por static folder
        custom_temp_dir = "./static"
        with tempfile.NamedTemporaryFile(
            delete=False, dir=custom_temp_dir
        ) as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name
            loader = Loader(temp_file_path)
            documents = loader.load()
            text_splitter = (
                RecursiveCharacterTextSplitter()
            )  # Assuming text_splitter is defined somewhere
            docs = text_splitter.split_documents(documents)

            for i, doc in enumerate(docs):
                doc.metadata["source"] = f"source_{i}"

            # Llama al segundo endpoint para almacenar los documentos en Redis
            # response = await store_documents(docs)
            # print(type(docs))
            return docs
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/store-documents")
async def store_documents(
    docs: List[Dict[str, Union[str, Dict[str, Union[str, int]]]]]
):
    try:
        # Convert each document to a serializable format (e.g., dictionary)
        serializable_docs = []
        for i, doc in enumerate(docs):
            serializable_doc = {
                "page_content": doc["page_content"],
                "metadata": doc["metadata"],
                "type": doc["type"],
                # Add other fields as needed
            }
            serializable_docs.append(serializable_doc)

            redis_key = f"document_{i}"
            serialized_data = json.dumps(serializable_doc)
            redis_client.set(redis_key, serialized_data)

        return {"message": "Documents stored in Redis"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error loading vector stores: {str(e)}",
        )


@router.get("/retrieve-all-documents")
async def retrieve_all_documents():
    try:
        # Get all keys that match the pattern
        keys = redis_client.keys("document_*")

        # Retrieve values for each key
        retrieved_docs = []
        for key in keys:
            serialized_data = redis_client.get(key)
            retrieved_doc = json.loads(serialized_data)
            retrieved_docs.append(retrieved_doc)

        return retrieved_docs
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error retrieving all documents from Redis: {str(e)}",
        )


@router.get("/retrieve-document/{document_id}")
async def retrieve_document(document_id: int):
    try:
        redis_key = f"document_{document_id}"
        serialized_data = redis_client.get(redis_key)

        if serialized_data is not None:
            retrieved_doc = json.loads(serialized_data)
            return retrieved_doc
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found in Redis",
            )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error retrieving document from Redis: {str(e)}",
        )
