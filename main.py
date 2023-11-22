import pandas as pd

# import matplotlib.pyplot as plt
import numpy as np
import os
import asyncio
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Query,
    Depends,
    status,
)

# import openpyxl
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import requests

# from typing import List

# import websockets

# from sockets import sio_app
from fastapi.staticfiles import StaticFiles


# from kbs.pdf_loader import router as pdf_loader_router
from auth.login import router as auth_router


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# from DB import connect_to_db, disconnect_from_db
# from sqlalchemy import create_engine, MetaData, Table

from DB import Base, engine, get_db, db_url
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models import Afiliado
from sqlalchemy import func
import re
import pdfminer

from pdfminer.high_level import extract_text

# from sqlalchemy.ext.declarative import declarative_base

# from auth.login import get_login_router

app = FastAPI()
# Define allowed origins (you should adjust this according to your requirements)
origins = [
    "*"
]  # "http://localhost",# "http://localhost:3000",  # Replace this with the actual URL of your Next.js app

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can specify HTTP methods like ["GET", "POST"]
    allow_headers=["*"],  # You can specify headers if needed
)
# app.mount("/", app=sio_app)
# Incluye las rutas de autenticación en tu aplicación principal
app.include_router(auth_router, tags=["auth"])
# app.include_router(pdf_loader_router, prefix="/kb", tags=["kb"])
# app.add.middleware(SessionMiddleware, secret_key="The secret key for testing")


# Creamos la sesión de SQLAlchemy

# engine = create_engine(db_url)


def create_tables():
    Base.metadata.create_all(bind=engine)


create_tables()


# Ruta para obtener un afiliado por su ID
@app.get("/afiliados-pdf")
async def obtener_afiliado(afiliado_id: int, db: Session = Depends(get_db)):
    text = extract_text(".\static\planillas\CAMILO ANDRES CASTRILLON CALDERON.pdf")
    print(text)


# Ruta para obtener un afiliado por su ID
@app.get("/afiliados/{afiliado_id}")
async def obtener_afiliado(afiliado_id: int, db: Session = Depends(get_db)):
    afiliado = db.execute(
        "SELECT * FROM afiliados WHERE id = :id", {"id": afiliado_id}
    ).first()
    if not afiliado:
        raise HTTPException(status_code=404, detail="Afiliado no encontrado")
    return afiliado


@app.get("/afiliados/")
async def obtener_afiliados(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    # -> List[Afiliado]:
    afiliados = db.query(Afiliado).offset(skip).limit(limit).all()
    return afiliados


@app.get("/afiliados/count")
async def contar_afiliados(db: Session = Depends(get_db)):
    count = db.query(func.count(Afiliado.id)).scalar()
    if count is None:
        raise HTTPException(status_code=404, detail="No se encontraron afiliados")
    return {"count": count}


@app.get("/")
async def main_2():
    try:
        print("main")
        return {"hello": "world"}
    except Exception as e:
        return f"error: {e}"


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         conn = await connect_to_db()  # Connect to the database

#         contents = await file.read()
#         df = pd.read_excel(contents)

#         # Insert data into the "usuarios" table
#         df.to_sql("usuarios", conn, if_exists="append", index=False)

#         await disconnect_from_db(conn)  # Disconnect from the database

#         return {"detail": "File uploaded successfully"}

#     except Exception as e:
#         # Catch any unexpected errors and return a meaningful response
#         print(str(e))
#         error_message = f"An error occurred: {str(e)}"
#         raise HTTPException(status_code=500, detail=error_message)


#


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
