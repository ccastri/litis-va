import pandas as pd
import matplotlib.pyplot as plt
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
import openpyxl
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sockets import sio_app
import requests
import websockets
from sockets import sio_app
from fastapi.staticfiles import StaticFiles
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from kbs.pdf_loader import router as pdf_loader_router
from auth.login import router as auth_router


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client


app = FastAPI()
# Define allowed origins (you should adjust this according to your requirements)
origins = [
    "http://localhost",
    "http://localhost:3000",  # Replace this with the actual URL of your Next.js app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can specify HTTP methods like ["GET", "POST"]
    allow_headers=["*"],  # You can specify headers if needed
)
# app.mount("/", app=sio_app)
# Incluye las rutas de autenticación en tu aplicación principal
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(pdf_loader_router, prefix="/kb", tags=["kb"])

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()

# # Assuming you have already authenticated and configured GoogleAuth
# drive = GoogleDrive(gauth)


@app.get("/")
async def main():
    try:
        print("yoooo!")
        return {"hello": "world"}
    except Exception as e:
        return f"error: {e}"


# def list_all_files():
#     try:
#         file_list = drive.ListFile().GetList()
#         all_files = []

#         for file in file_list:
#             all_files.append(
#                 {
#                     "title": file["title"],
#                     "id": file["id"]
#                     # You can add more file details if needed
#                 }
#             )

#         return all_files
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


# def get_file_by_title(title: str, files_list: list):
#     for file in files_list:
#         if file["title"] == title:
#             return file
#     return None


# @app.get("/list-all-files")
# async def list_all_drive_files(
#     # title: str = Query(..., title="File Title")
#     title: str = "output_file",
# ):
#     try:
#         all_files = list_all_files()
#         requested_file = get_file_by_title(title, all_files)

#         if requested_file:
#             return JSONResponse(content=requested_file)
#         else:
#             raise HTTPException(
#                 status_code=404, detail=f"File with title '{title}' not found."
#             )
#     except HTTPException as e:
#         return JSONResponse(content={"error": e.detail}, status_code=e.status_code)


# async def list_all_drive_files():
#     try:
#         all_files = list_all_files()
#         return JSONResponse(content=all_files)
#     except HTTPException as e:
#         return JSONResponse(content={"error": e.detail}, status_code=e.status_code)

mimetypes = {
    # Drive Document files as MS Word files.
    "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Drive Sheets files as MS Excel files.
    "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    # etc.
}


# def download_file(file_id: str, download_folder: str):
#     try:
#         file = drive.CreateFile({"id": file_id})
#         filename = file["title"]

#         # Make sure the download folder exists
#         os.makedirs(download_folder, exist_ok=True)

#         mimetypes = {
#             "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#             "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             # Add more MIME types as needed
#         }

#         download_mimetype = mimetypes.get(file["mimeType"], None)

#         if download_mimetype:
#             file.GetContentFile(
#                 os.path.join(download_folder, filename), mimetype=download_mimetype
#             )
#         else:
#             file.GetContentFile(os.path.join(download_folder, filename))

#         return filename
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


# @app.get("/download-file/{file_id}")
# async def download_drive_file(file_id: str):
#     try:
#         file_name = download_file(file_id, "/static")
#         full_path = os.path.join("/static", file_name)
#         return StreamingResponse(
#             open(full_path, "rb"),
#             media_type="application/octet-stream",
#             headers={"Content-Disposition": f"attachment;filename={file_name}"},
#         )
#     except HTTPException as e:
#         return {"error": e.detail}


# def access_google_drive(file_id: str = "10hVrKmMzQ-YumgQVJ3gDq_i9Fv1wdiBp1hPAO7wt2vk"):
#     try:
#         # No necesitas cargar las credenciales aquí si ya has autenticado con PyDrive
#         # Crea una instancia del servicio de Google Drive
#         drive_service = build("drive", "v3", credentials=gauth.credentials)

#         # Accede al archivo Excel sin descargarlo
#         response = (
#             drive_service.files()
#             .export(
#                 fileId=file_id,
#                 mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             )
#             .execute()
#         )

#         # Procesa el contenido según tus necesidades, por ejemplo, carga en un DataFrame de pandas
#         excel_data = BytesIO(response)
#         df = pd.read_excel(excel_data)

#         # # Convertir columnas de tipo Timestamp a cadenas de texto
#         date_columns = [
#             "Fecha Nacimiento",
#             "Fecha Expedición",
#             "Fecha Afiliación",
#             "Fecha_Ultimo_Pago",
#         ]
#         for col in date_columns:
#             df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

#         # Limpiar valores flotantes para evitar errores de serialización JSON
#         df.replace([np.inf, -np.inf], np.nan, inplace=True)
#         df.fillna(0, inplace=True)  # Puedes ajustar esto según tus necesidades

#         # Seleccionar solo las columnas de interés
#         columns_of_interest = [
#             "Tipo Identificacion",
#             "Identificación",
#             "Primer Nombre",
#             "Segundo Nombre",
#             "Primer Apellido",
#             "Segundo Apellido",
#             "Numero Celular",
#             "Email",
#             "Link_Planillas",
#             "Pago_Realizado",
#             "Fecha_Ultimo_Pago",
#         ]

#         df_subset = df[(df["Pago_Realizado"] == "SI") & (df["Fecha_Ultimo_Pago"] != 0)]

#         # Iterar sobre cada fila del subconjunto filtrado y enviar el correo a cada usuario
#         # for index, user in df_subset.iterrows():
#         #     # Enviar el enlace del archivo por WhatsApp
#         #     enviar_pdf_desde_google_drive(
#         #         f"Link de la planilla: {user['Link_Planillas']}",
#         #         # user["Numero Celular"],
#         #         # user["Primer Nombre"],
#         #         user[
#         #             "Email"
#         #         ],  # Asumiendo que 'Numero Celular' contiene el número de WhatsApp
#         #     )

#         return df_subset
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error accessing Google Drive: {str(e)}"
#         )


# @app.get("/access-google-drive/{file_id}")
# async def access_google_drive_endpoint(
#     file_id: str = "10hVrKmMzQ-YumgQVJ3gDq_i9Fv1wdiBp1hPAO7wt2vk",
# ):
#     try:
#         result_df = access_google_drive(file_id)
#         return JSONResponse(content=result_df.to_dict(orient="records"))
#     except HTTPException as e:
#         return JSONResponse(content={"error": e.detail}, status_code=e.status_code)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)


# Función para descargar y enviar un archivo PDF desde Google Drive por correo electrónico
# def enviar_pdf_desde_google_drive(
#     file_link: str,
#     #   name_sender: str,
#     email: str,
#     provider: str = "gmail",
# ):
#     # Configurar la autenticación de PyDrive
#     # Obtener el ID del archivo desde el enlace de Google Drive
#     # file_id = file_link.split("/")[-2]
#     # filename = f"{name_sender}.pdf"

#     gauth = GoogleAuth()
#     gauth.LocalWebserverAuth()

#     # Autenticar con Google Drive
#     drive = GoogleDrive(gauth)

#     try:
#         # file = drive.CreateFile({"id": file_id})
#         # file.GetContentFile(filename)  # Descargar el archivo PDF

#         # Configurar los parámetros para enviar el correo electrónico
#         from_address = "cycaccionlegalsas@gmail.com"
#         password = "kvbs wfum qrst bvsx"
#         to_address = email

#         msg = MIMEMultipart()
#         msg["From"] = from_address
#         msg["To"] = to_address
#         msg[
#             "Subject"
#         ] = "Envio de planilla automatizado desde Google Drive. Bechos gordito"

#         # Configurar el servidor SMTP y envío del correo electrónico según el proveedor
#         if provider.lower() == "gmail":
#             smtp_server = "smtp.gmail.com"
#             port = 587
#         elif provider.lower() == "hotmail":
#             smtp_server = "smtp.live.com"  # Puedes usar "smtp.office365.com" si es una cuenta de Office 365
#             port = 587
#         else:
#             raise ValueError("Proveedor de correo no compatible")
#         # Adjuntar el archivo PDF al correo electrónico       # Cuerpo del correo con el enlace del archivo de Google Drive
#         body = f"Estimado/a,\n\nAquí está el enlace al archivo: {file_link}\n\nAtentamente,\nTu empresa"
#         msg.attach(MIMEText(body, "plain"))
#         # Configuración del servidor SMTP y envío del correo electrónico
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(from_address, password)
#         server.send_message(msg)
#         server.quit()

#         print("Correo electrónico enviado con el archivo adjunto.")

#     except Exception as e:
#         print(f"Error: {str(e)}")
