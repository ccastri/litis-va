from datetime import datetime
import pandas as pd

# import matplotlib.pyplot as plt
import numpy as np
# import xlwt
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
    Request,
    Response,
)
from starlette.responses import FileResponse
import zipfile

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
from routers.empleados import router as empleados_router


# Migrar a tareas del drive
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from io import BytesIO

# TODO: Migrar a utils/ai/tools/email_tasks.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from DB import Base, engine, get_db, db_url
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models import *
# from models.messaging import Message
from sqlalchemy import func
import re
import psycopg2

# import pdfminer.six

# from pdfminer.high_level import extract_text

import urllib.parse
import tempfile

import schemas 
import models 
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
openapi_url="/api/openapi.json",
docs_url="/api/docs"
)
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
app.include_router(empleados_router,  tags=["empleados"])
# app.include_router(pdf_loader_router, prefix="/kb", tags=["kb"])
# app.add.middleware(SessionMiddleware, secret_key="The secret key for testing")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Creamos la sesión de SQLAlchemy
def create_tables():
    Base.metadata.create_all(bind=engine)


create_tables()






@app.get("/api/health")
async def main_2():
    try:
        print("main")
        return {"hello": "worlddddd"}
    except Exception as e:
        return f"error: {e}"







if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)









def enviar_pdf(
    correo: str,
    pdf_content: bytes,
    file_name: str,
    provider: str,
):
    try:
        from_address = (
            os.getenv("SMTP_EMAIL") # Cambia esto con tu dirección de correo
        )
        password = os.getenv("SMT_PASSWORD")  # Cambia esto con tu contraseña

        # Crear instancia del mensaje
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = correo
        msg["Subject"] = "Reporte pago {ID del reporte} {mes}{año} su planilla"

        # Configurar el servidor SMTP y envío del correo electrónico según el proveedor
        if provider.lower() == "gmail.com":
            smtp_server = "smtp.gmail.com"
            port = os.getenv("PORT")
        elif provider.lower() == "hotmail.com":
            smtp_server = "smtp.live.com"  # Puedes usar "smtp.office365.com" si es una cuenta de Office 365
            port = os.getenv("PORT")
        else:
            raise ValueError("Proveedor de correo no compatible")

        # Cuerpo del correo
        body = "Este es el reporte de la planilla"
        msg.attach(MIMEText(body, "plain"))

        # Adjuntar el archivo PDF
        part = MIMEBase("application", "octet-stream")
        part.set_payload(pdf_content)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}",
        )
        msg.attach(part)

        # Configurar el servidor SMTP y enviar el correo electrónico
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(from_address, password)
        server.send_message(msg)
        server.quit()

        print("Correo electrónico enviado con el archivo adjunto.")

    except Exception as e:
        print(f"Error: {str(e)} {correo}")


@app.post("/enviar-archivos")
async def enviar_archivos_a_afiliados(uploaded_file: UploadFile = File(...)):
    try:
        # Leer el archivo .zip
        zip_file = await uploaded_file.read()

        # Crear un objeto ZipFile
        with zipfile.ZipFile(BytesIO(zip_file), "r") as zip_ref:
            # Buscar el archivo .csv dentro del .zip
            csv_file_name = next(
                (
                    file_name
                    for file_name in zip_ref.namelist()
                    if file_name.lower().endswith(".csv")
                ),
                None,
            )

            # Si se encuentra el archivo .csv, procesarlo
            if csv_file_name:
                # Leer el contenido del archivo .csv con Pandas
                with zip_ref.open(csv_file_name) as csv_file:
                    df = pd.read_csv(csv_file)

                    # Iterar sobre cada fila del archivo .csv
                    for index, row in df.iterrows():
                        (
                            nombre_archivo,
                            correo,
                            primer_nombre,
                            primer_apellido,
                            numero_celular,
                        ) = row
                        print(row)
                        # Extraer el proveedor del correo electrónico
                        proveedor_correo = correo.split("@")[1]

                        # Buscar y enviar el archivo correspondiente a cada afiliado por correo
                        for file_name in zip_ref.namelist():
                            # print(file_name)
                            if (
                                file_name.lower().endswith(".pdf")
                                and nombre_archivo in file_name
                            ):
                                # Leer el contenido del archivo PDF
                                with zip_ref.open(file_name) as pdf_file:
                                    pdf_content = pdf_file.read()
                                    print(pdf_content)
                                    print(correo)
                                    # Enviar el archivo PDF por correo al afiliado
                                    enviar_pdf(
                                        correo,
                                        pdf_content,
                                        file_name,
                                        provider=proveedor_correo,
                                    )
    except Exception as e:
        return {"error": str(e)}













# @app.post("/afiliados-zip")
# async def obtener_planilla_afiliado_zip(
#     db: Session = Depends(get_db),
#     uploaded_file: UploadFile = File(...),
# ):
#     try:
#         zip_file = await uploaded_file.read()

#         csv_data = []
#         zip_output = BytesIO()

#         # Directorio temporal para extraer los archivos
#         temp_dir = "temp_directory"
#         os.makedirs(temp_dir, exist_ok=True)

#         with zipfile.ZipFile(BytesIO(zip_file), "r") as zip_ref:
#             for file_name in zip_ref.namelist():
#                 if file_name.lower().endswith(".pdf"):
#                     parts = file_name.split("_")
#                     cc_number = None

#                     for part in parts:
#                         if part.startswith("CC"):
#                             cc_number_match = re.search(r"\d+", part)
#                             if cc_number_match:
#                                 cc_number = cc_number_match.group()
#                             break

#                     if cc_number:
#                         afiliado_info = (
#                             db.query(
#                                 Afiliado.email,
#                                 Afiliado.primer_nombre,
#                                 Afiliado.primer_apellido,
#                                 Afiliado.numero_celular,
#                             )
#                             .filter(Afiliado.identificacion == cc_number)
#                             .first()
#                         )

#                         if afiliado_info:
#                             (
#                                 email,
#                                 primer_nombre,
#                                 primer_apellido,
#                                 numero_celular,
#                             ) = afiliado_info

#                             # nuevo_nombre = (
#                             #     f"{cc_number}_{primer_nombre}_{primer_apellido}.pdf"
#                             # )

#                             csv_data.append(
#                                 [
#                                     file_name,
#                                     email.lower(),
#                                     primer_nombre,
#                                     primer_apellido,
#                                     numero_celular,
#                                 ]
#                             )

#                             # Extraer el archivo al directorio temporal
#                             zip_ref.extract(file_name, temp_dir)

#         # Convertir los datos a un DataFrame de Pandas
#         df = pd.DataFrame(
#             csv_data,
#             columns=[
#                 "Nombre Archivo",
#                 "Correo",
#                 "Primer Nombre",
#                 "Primer Apellido",
#                 "Telefono",
#             ],
#         )

#         # Escribir el DataFrame a un archivo CSV
#         csv_output = BytesIO()
#         df.to_csv(csv_output, index=False)

#         with zipfile.ZipFile(zip_output, "w") as zf:
#             for file_name in os.listdir(temp_dir):
#                 file_path = os.path.join(temp_dir, file_name)
#                 if os.path.isfile(file_path):
#                     zf.write(file_path, file_name)  # Agregar archivo al ZIP

#             # Agregar el archivo CSV al ZIP
#             zf.writestr("nombres_correos.csv", csv_output.getvalue())

#         # Eliminar el directorio temporal
#         for file in os.listdir(temp_dir):
#             os.remove(os.path.join(temp_dir, file))
#         os.rmdir(temp_dir)

#         # Preparar la respuesta como archivo ZIP
#         zip_output.seek(0)
#         response = StreamingResponse(zip_output, media_type="application/zip")
#         response.headers[
#             "Content-Disposition"
#         ] = "attachment; filename=archivos_renombrados.zip"

#         return response

#     except Exception as e:
#         return {"error": str(e)}


# @app.get(
#     "/afiliados/",
#     #  response_model=Dict[str, any]
# )
# async def obtener_afiliados(
#     skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
# ):
#     afiliados = db.query(Afiliado).offset(skip).limit(limit).all()
#     afiliados_length = db.query(Afiliado).count()
#     print(afiliados)
#     print(afiliados_length)

#     return {"afiliados": afiliados, "cantidad": afiliados_length}


# @app.get("/afiliados/")
# async def obtener_afiliados(
#     skip: Optional[str] = 0,
#     limit: Optional[str] = 0,
#     orden: Optional[str] = Query(None),
#     eps: Optional[str] = Query(None),
#     afp: Optional[str] = Query(None),
#     identificacion: Optional[str] = Query(None),
#     riesgo: Optional[int] = Query(None),
#     db: Session = Depends(get_db),
# ):
#     eps_decoded = urllib.parse.unquote_plus(eps) if eps else None
#     query = db.query(Afiliado)
#     # query = db.query(Afiliado).offset(skip).limit(limit).all()

#     # Aplicar filtros según los parámetros proporcionados
#     if orden:
#         if orden == "A-Z":
#             query = query.order_by(Afiliado.primer_apellido.asc())
#         elif orden == "Z-A":
#             query = query.order_by(Afiliado.primer_apellido.desc())

#     if eps_decoded and eps_decoded != "":
#         query = query.filter(Afiliado.eps == eps_decoded)

#     if afp is not None:
#         if afp == "null":
#             query = query.filter(Afiliado.afp.is_(None))
#         elif afp != "":  # Verificar si el valor no es una cadena vacía
#             query = query.filter(Afiliado.afp == afp)

#     if identificacion:
#         query = query.filter(Afiliado.identificacion == int(identificacion))

#     if riesgo is not None:
#         if riesgo != "":
#             query = query.filter(Afiliado.arl_nivel == int(riesgo))

#     afiliados = query.offset(skip).limit(limit).all()
#     afiliados_length = query.count()

#     return {"afiliados": afiliados, "cantidad": afiliados_length}


# @app.get("/afiliados/documentos/")
# async def obtener_documentos_afiliados(
#     selected_ids: Optional[List[int]] = Query(None),
#     page_size: int = 10,
#     skip: int = 0,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(
#         Afiliado.tipo_identificacion, Afiliado.identificacion, Afiliado.afp
#     )

#     # Filtra los afiliados seleccionados si se proporcionan los IDs
#     if selected_ids:
#         query = query.filter(Afiliado.id.in_(selected_ids))

#     # Aplica la paginación después del filtrado
#     query = query.offset(skip).limit(page_size)

#     afiliados = query.all()

#     documentos_afiliados = [
#         DocumentoAfiliado(
#             tipo_identificacion=afi[0],
#             identificacion=afi[1],
#             afp=afi[2],
#         )
#         for afi in afiliados
#     ]

#     return documentos_afiliados


# # Ruta para obtener un afiliado por su ID
# @app.get("/afiliados/{afiliado_id}")
# async def obtener_afiliado(afiliado_id: int, db: Session = Depends(get_db)):
#     afiliado = db.execute(
#         "SELECT * FROM afiliados WHERE id = :id", {"id": afiliado_id}
#     ).first()
#     if not afiliado:
#         raise HTTPException(status_code=404, detail="Afiliado no encontrado")
#     return afiliado


# @app.post("/api/generar-xls")
# async def generar_xls(request: Request):
#     data = await request.json()

#     # Supongamos que 'data' tiene la estructura de tus datos de afiliados

#     # Crear un DataFrame de Pandas con los datos
#     # df = pd.DataFrame(data)

#     # Obtener la lista de afiliados desde 'selectedAfiliados'
#     afiliados = data.get(
#         "selectedAfiliados", []
#     )  # Obtener la lista de afiliados, si está presente

#     # Crear un DataFrame de Pandas con los datos de los afiliados
#     df = pd.DataFrame(afiliados)
#     # print(df.columns)

#     # Seleccionar solo las columnas 'tipo_identificacion' y 'identificacion'
#     df_filtered = df[["tipo_identificacion", "identificacion"]]

#     # Crear un libro de Excel
#     book = xlwt.Workbook(encoding="utf-8")
#     sheet = book.add_sheet("Sheet 1")

#     # Escribir los datos en el libro de Excel
#     for i, (_, row) in enumerate(
#         df_filtered.iterrows()
#     ):  # Utilizamos _ para ignorar el índice
#         sheet.write(i, 0, str(row["tipo_identificacion"]))
#         sheet.write(i, 1, str(row["identificacion"]))

#     # Guardar el libro de Excel en un buffer de BytesIO
#     excel_data = BytesIO()
#     book.save(excel_data)
#     excel_data.seek(0)

#     # Return the Excel file as a StreamingResponse
#     # return "done"
#     return StreamingResponse(
#         iter([excel_data.getvalue()]),
#         media_type="application/vnd.ms-excel",
#         headers={"Content-Disposition": "attachment; filename=datos.xls"},
#     )
