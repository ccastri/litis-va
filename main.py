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

from typing import List, Optional

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
from models import Afiliado, DocumentoAfiliado
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
async def obtener_planilla_afiliado(afiliado_id: int, db: Session = Depends(get_db)):
    text = extract_text(".\static\planillas\CAMILO ANDRES CASTRILLON CALDERON.pdf")
    print(text)


@app.get("/afiliados/count")
async def contar_afiliados(db: Session = Depends(get_db)):
    try:
        count = db.query(func.count()).select_from(Afiliado).scalar()
        if count is None:
            raise HTTPException(status_code=404, detail="No se encontraron afiliados")
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/afiliados/documentos/")
# async def obtener_documentos_afiliados(
#     skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
# ):
#     # -> List[DocumentoAfiliado]:
#     afiliados = (
#         db.query(Afiliado.tipo_identificacion, Afiliado.identificacion)
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )
#     documentos_afiliados = [
#         DocumentoAfiliado(
#             tipo_identificacion=afi.tipo_identificacion,
#             identificacion=afi.identificacion,
#         )
#         for afi in afiliados
#     ]

#     return documentos_afiliados


@app.get("/afiliados/documentos/")
async def obtener_documentos_afiliados(
    selected_ids: Optional[List[int]] = Query(None),
    page_size: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Afiliado.tipo_identificacion, Afiliado.identificacion)

    # Filtra los afiliados seleccionados si se proporcionan los IDs
    if selected_ids:
        query = query.filter(Afiliado.id.in_(selected_ids))

    # Aplica la paginación después del filtrado
    query = query.offset(skip).limit(page_size)

    afiliados = query.all()

    documentos_afiliados = [
        DocumentoAfiliado(
            tipo_identificacion=afi[0],
            identificacion=afi[1],
        )
        for afi in afiliados
    ]

    return documentos_afiliados


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
