import pandas as pd

# import matplotlib.pyplot as plt
import numpy as np
import xlwt
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

# import pdfminer.six

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
# @app.get("/afiliados-pdf")
# async def obtener_planilla_afiliado(afiliado_id: int, db: Session = Depends(get_db)):
#     text = extract_text(".\static\planillas\CAMILO ANDRES CASTRILLON CALDERON.pdf")
#     print(text)
@app.post("/afiliados-zip")
async def obtener_planilla_afiliado_zip(uploaded_file: UploadFile = File(...)):
    try:
        zip_file = await uploaded_file.read()

        pdf_files_texts = []

        # Extract and process each PDF file within the ZIP
        with zipfile.ZipFile(BytesIO(zip_file), "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(".pdf"):
                    # Read the PDF file from the ZIP
                    with zip_ref.open(file_name) as pdf_file:
                        # Extract text from the second page of the PDF using pdfminer
                        pdf_content = pdf_file.read()
                        text = extract_text(BytesIO(pdf_content), page_numbers=[1])
                        pdf_files_texts.append((file_name, text))

        return {
            "message": "Text extracted from the second page of PDF files in the ZIP",
            "pdf_files_texts": pdf_files_texts,
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/afiliados-pdf")
async def obtener_planilla_afiliado(uploaded_files: List[UploadFile] = File(...)):
    try:
        renamed_files = []

        for uploaded_file in uploaded_files:
            file_bytes = await uploaded_file.read()

            # Extraer solo la segunda página del archivo PDF
            second_page_text = extract_text(BytesIO(file_bytes), page_numbers=[1])

            # Patrones de expresiones regulares para la información que deseas extraer
            patrones = {
                "Periodo Cotización": r"Periodo Cotización\s*\n+([\w\d]+)",
                "Periodo Servicio": r"Periodo Servicio\s*\n+([\w\d]+)",
                "Tipo Planilla": r"Tipo Planilla\s*\n+([\w\d]+)",
                "Documento": r"Documento\s*\n\n([A-Z0-9 ]+)",
                "Nombre del Afiliado": r"Nombres y Apellidos\s*\n\n([A-Z ]+)",
            }

            # Función para extraer la información basada en los patrones definidos
            def extraer_informacion(texto):
                info_extraida = {}
                for nombre, patron in patrones.items():
                    resultado = re.search(patron, texto)
                    if resultado:
                        info_extraida[nombre] = resultado.group(1)
                    else:
                        info_extraida[nombre] = None
                return info_extraida

            # Extraer la información del texto de la segunda página
            info_extraida = extraer_informacion(second_page_text)

            # Renombrar el archivo según la información extraída
            nuevo_nombre = f"{info_extraida['Documento']}_{info_extraida['Nombre del Afiliado']}_{info_extraida['Tipo Planilla']}_{info_extraida['Periodo Cotización']}_{info_extraida['Periodo Servicio']}.pdf"

            # Guardar el archivo con el nuevo nombre
            with open(nuevo_nombre, "wb") as file_object:
                file_object.write(file_bytes)

            renamed_files.append((nuevo_nombre, file_bytes))

        # Crear un archivo zip con los archivos renombrados
        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, "w") as zf:
            for nombre, contenido in renamed_files:
                zf.writestr(nombre, contenido)

        # Configurar la respuesta como un archivo zip
        zip_file.seek(0)
        response = StreamingResponse(zip_file, media_type="application/zip")
        response.headers[
            "Content-Disposition"
        ] = "attachment; filename=archivos_renombrados.zip"

        return response

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get(
    "/afiliados/",
    #  response_model=Dict[str, any]
)
async def obtener_afiliados(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    afiliados = db.query(Afiliado).offset(skip).limit(limit).all()
    afiliados_length = db.query(Afiliado).count()
    print(afiliados)

    # return {
    #     "afiliados": afiliados,
    #     "cantidad": afiliados_length
    # }
    return afiliados


@app.get("/afiliados/count")
async def contar_afiliados(db: Session = Depends(get_db)):
    try:
        count = db.query(func.count()).select_from(Afiliado).scalar()
        if count is None:
            raise HTTPException(status_code=404, detail="No se encontraron afiliados")
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


# @app.get("/afiliados/")
# async def obtener_afiliados(
#     skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
# ):
#     # -> List[Afiliado]:
#     afiliados = db.query(Afiliado).offset(skip).limit(limit).all()
#     afiliados_length = db.query(Afiliado).count()
#     return {"afiliados": afiliados, "cantidad": afiliados_length}

# @app.post("/api/generar-csv")
# async def generar_csv(selected_afiliados: List[Dict[str, str]]):
#     if not selected_afiliados:
#         raise HTTPException(status_code=400, detail="No se han proporcionado afiliados seleccionados")

#     # Lógica para buscar instancias coincidentes en la base de datos utilizando selected_afiliados

#     # Ejemplo de datos ficticios para generar un archivo CSV
#     datos_a_csv = [
#         {"Tipo de Documento": afiliado["tipo_identificacion"], "Número de Documento": afiliado["identificacion"]}
#         for afiliado in selected_afiliados
#     ]

#     # Crear el archivo CSV en memoria
#     output = io.StringIO()
#     csv_writer = csv.DictWriter(output, fieldnames=["Tipo de Documento", "Número de Documento"])
#     csv_writer.writeheader()
#     csv_writer.writerows(datos_a_csv)

#     # Regresar el archivo CSV como respuesta
#     output.seek(0)
#     return StreamingResponse(iter([output.getvalue()]), media_type="text/csv")


@app.post("/api/generar-xls")
async def generar_xls(request: Request):
    data = await request.json()

    # Supongamos que 'data' tiene la estructura de tus datos de afiliados

    # Crear un DataFrame de Pandas con los datos
    # df = pd.DataFrame(data)

    # Obtener la lista de afiliados desde 'selectedAfiliados'
    afiliados = data.get(
        "selectedAfiliados", []
    )  # Obtener la lista de afiliados, si está presente

    # Crear un DataFrame de Pandas con los datos de los afiliados
    df = pd.DataFrame(afiliados)
    # print(df.columns)

    # Seleccionar solo las columnas 'tipo_identificacion' y 'identificacion'
    df_filtered = df[["tipo_identificacion", "identificacion"]]

    # Crear un libro de Excel
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("Sheet 1")

    # Escribir los datos en el libro de Excel
    for i, (_, row) in enumerate(
        df_filtered.iterrows()
    ):  # Utilizamos _ para ignorar el índice
        sheet.write(i, 0, str(row["tipo_identificacion"]))
        sheet.write(i, 1, str(row["identificacion"]))

    # Guardar el libro de Excel en un buffer de BytesIO
    excel_data = BytesIO()
    book.save(excel_data)
    excel_data.seek(0)

    # Return the Excel file as a StreamingResponse
    # return "done"
    return StreamingResponse(
        iter([excel_data.getvalue()]),
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": "attachment; filename=datos.xls"},
    )


# def obtener_correos_afiliados(db: Session, selected_ids: List[int]) -> List[Tuple[str]]:
#     # Consulta para obtener los correos electrónicos de los afiliados según los IDs proporcionados
#     correos_afiliados = (
#         db.query(Afiliado.identificacion, Afiliado.email)
#         .filter(Afiliado.id.in_(selected_ids))
#         .all()
#     )

#     return correos_afiliados


# @app.get("/afiliados/enviar-email/")
# async def obtener_documentos_afiliados(
#     selected_ids: List[int] = Query(...),
#     # ... otros parámetros
#     db: Session = Depends(get_db),
# ):
#     # Utiliza la función para obtener los correos electrónicos
#     correos_afiliados = obtener_correos_afiliados(db, selected_ids)

# Resto del código para devolver documentos_afiliados...


def enviar_pdf(
    file_path: str,
    to_address: str,
    provider: str = "gmail",
):
    try:
        from_address = (
            "cycaccionlegalsas@gmail.com"  # Cambia esto con tu dirección de correo
        )
        password = "kvbs wfum qrst bvsx"  # Cambia esto con tu contraseña
        to_address = to_address

        # Crear instancia del mensaje
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = to_address
        msg["Subject"] = "Reporte pago de su planilla"

        # Configurar el servidor SMTP y envío del correo electrónico según el proveedor
        if provider.lower() == "gmail":
            smtp_server = "smtp.gmail.com"
            port = 587
        elif provider.lower() == "hotmail":
            smtp_server = "smtp.live.com"  # Puedes usar "smtp.office365.com" si es una cuenta de Office 365
            port = 587
        else:
            raise ValueError("Proveedor de correo no compatible")
        # Cuerpo del correo
        body = "Este es el reporte de la planilla"
        msg.attach(MIMEText(body, "plain"))

        # Adjuntar el archivo PDF
        filename = file_path
        attachment = open(filename, "rb")
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)

        # Configurar el servidor SMTP y enviar el correo electrónico
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_address, password)
        server.send_message(msg)
        server.quit()

        print("Correo electrónico enviado con el archivo adjunto.")

    except Exception as e:
        print(f"Error: {str(e)}")


# def enviar_correo_a_afiliados(
#     file_link: str,
#     selected_ids: List[int],
#     db: Session = Depends(get_db),
# ):
#     try:
#         # Obtener los correos electrónicos
#         correos_afiliados = obtener_correos_afiliados(db, selected_ids)

#         # Iterar sobre los correos electrónicos y enviar el correo a cada uno
#         for identificacion, email in correos_afiliados:
#             enviar_pdf(file_link, email)

#         print("Correos electrónicos enviados a los afiliados.")

#     except Exception as e:
#         print(f"Error: {str(e)}")


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
