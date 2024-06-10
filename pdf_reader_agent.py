from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
from fastapi import APIRouter



router = APIRouter()
load_dotenv()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
embeddings = OpenAIEmbeddings()


class FileInput(BaseModel):
    type: str
    content: bytes


def process_file(file_input: File):
    Loader = TextLoader if file_input.type == "text/plain" else PyPDFLoader
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_input.content)
        temp_file_path = temp_file.name

    loader = Loader(temp_file_path)
    documents = loader.load()
    docs = text_splitter.split_documents(documents)

    for i, doc in enumerate(docs):
        doc.metadata["source"] = f"source_{i}"

    return docs


def get_docsearch(docs):
    docsearch = Chroma.from_documents(docs, embeddings)
    return docsearch


@router.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_content = await file.read()
    file_input = FileInput(type=file.content_type, content=file_content)

    # Process the file in the background
    background_tasks.add_task(process_and_index_file, file_input)

    return JSONResponse(
        content={"message": "File processing started in the background."}
    )


def process_and_index_file(file_input: FileInput):
    docs = process_file(file_input)
    docsearch = get_docsearch(docs)
    # Additional processing or indexing steps can be added here

    # Example: Print the first document's content
    print(docs[0].page_content)
