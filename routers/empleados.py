from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
# from app import schemas, models, db
import schemas 
import models 
from DB import SessionLocal
from sqlalchemy.orm import Session
import httpx
from routers.selenium_aportes_en_linea import *
router = APIRouter(

)
import time
# Función para obtener la sesión actual
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




        
# TODO: WE GOT TO IMPLEMENT TRY CATCH FOR EXCEPTION HANDLING


@router.post("/api/nuevo_empleado", response_model=schemas.EmpleadoSchema)
def create_empleado(empleado: schemas.EmpleadoSchema, db: Session = Depends(get_db)):
    db_empleado = models.Empleado(
        tipo_identificacion=empleado.tipo_identificacion,
        identificacion=empleado.identificacion,
        primer_nombre=empleado.primer_nombre,
        segundo_nombre=empleado.segundo_nombre,
        primer_apellido=empleado.primer_apellido,
        segundo_apellido=empleado.segundo_apellido,
        tipo_sexo=empleado.tipo_sexo,
        cotizante_extranjero=empleado.cotizante_extranjero,
        fecha_nacimiento=empleado.fecha_nacimiento,
        edad=empleado.edad,
        fecha_expedicion=empleado.fecha_expedicion,
        incapacidades=empleado.incapacidades,
    )

    # Añadir detalles de contacto
    for detalle in empleado.detalles_contacto:
        db_detalle_contacto = models.DetalleContacto(**detalle.dict())
        db_empleado.detalles_contacto.append(db_detalle_contacto)

    # Añadir detalles de salario
    for detalle in empleado.detalles_salario:
        db_detalle_salario = models.DetalleSalario(**detalle.dict())
        db_empleado.detalles_salario.append(db_detalle_salario)

    # Añadir detalles de afiliación
    for detalle in empleado.detalles_afiliacion:
        db_detalle_afiliacion = models.DetalleAfiliacion(**detalle.dict())
        db_empleado.detalles_afiliacion.append(db_detalle_afiliacion)

    db.add(db_empleado)
    db.commit()
    db.refresh(db_empleado)
    return db_empleado

@router.get("/api/empleados/{empleado_id}", response_model=schemas.EmpleadoSchema)
def read_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = db.query(models.Empleado).filter(models.Empleado.id == empleado_id).first()
    empleado_dict = {
        "id": empleado.id,
        "tipo_identificacion": empleado.tipo_identificacion,
        "identificacion": empleado.identificacion,
        "primer_nombre": empleado.primer_nombre,
        "segundo_nombre": empleado.segundo_nombre,
        "primer_apellido": empleado.primer_apellido,
        "segundo_apellido": empleado.segundo_apellido,
        "tipo_sexo": empleado.tipo_sexo,
        "cotizante_extranjero": empleado.cotizante_extranjero,
        "fecha_nacimiento": empleado.fecha_nacimiento,
        "edad": empleado.edad,
        "fecha_expedicion": empleado.fecha_expedicion,
        "incapacidades": empleado.incapacidades,
        # Puedes continuar agregando otros campos según sea necesario
        # Recuerda manejar los campos opcionales correctamente
    }

    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado not found")
    return empleado_dict
    # return {"empleados": empleado}

@router.get("/api/empleados", response_model=List[schemas.EmpleadoSchema])
def read_empleados(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    empleados = db.query(models.Empleado).offset(skip).limit(limit).all()
    empleado_dicts = []
    for empleado in empleados:
        empleado_dict = {
            "id": empleado.id,
            "tipo_identificacion": empleado.tipo_identificacion,
            "identificacion": empleado.identificacion,
            "primer_nombre": empleado.primer_nombre,
            "segundo_nombre": empleado.segundo_nombre,
            "primer_apellido": empleado.primer_apellido,
            "segundo_apellido": empleado.segundo_apellido,
            "tipo_sexo": empleado.tipo_sexo,
            "cotizante_extranjero": empleado.cotizante_extranjero,
            "fecha_nacimiento": empleado.fecha_nacimiento,
            "edad": empleado.edad,
            "fecha_expedicion": empleado.fecha_expedicion,
            "incapacidades": empleado.incapacidades,
            # Puedes continuar agregando otros campos según sea necesario
            # Recuerda manejar los campos opcionales correctamente
        }
        empleado_dicts.append(empleado_dict)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado not found")    
    return empleado_dicts


@router.get("/api/empleados-nc", )
async def get_afiliados(xc_auth: str = Header(...), xc_token: str = Header(...)):
    url = "http://172.17.0.1:8081/api/v2/tables/m7asitmd2npcerc/records?viewId=vwu86btadj6tnlpj&limit=25&shuffle=0&offset=0"
    headers = {
        'accept': 'application/json',
        'xc-auth': xc_auth,
        'xc-token': xc_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching afiliados")
        return response.json()
    
@router.get("/api/empleados-nc/{empleado_id}")
async def get_afiliados(empleado_id: int, xc_auth: str = Header(...), xc_token: str = Header(...)):
    url = f"http://172.17.0.1:8081/api/v2/tables/m7asitmd2npcerc/records/{empleado_id}"
    headers = {
        'accept': 'application/json',
        'xc-auth': xc_auth,
        'xc-token': xc_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            detail = f"Error fetching afiliados: {response.status_code} - {response.text}"
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json()
    
@router.post("/api/search_employees")
def search_employees_endpoint(empleado_id: str):
    URL="https://www.aportesenlinea.com/Home/home.aspx?ReturnUrl=%2fPagosMultiples.aspx%3fmaremplsid%3df0mqdlyd11jxbb3pqbquxbpy&maremplsid=f0mqdlyd11jxbb3pqbquxbpy"
    USERNAME = os.getenv("NIT")
    PASSWORD = os.getenv("PASSWORD")
    driver = setup_driver(URL)
    try:
        inicio = time.time()
        login(driver, USERNAME, PASSWORD)
        time.sleep(1)
        open_employees_search_form(driver)
        time.sleep(1)
        # for employee in empleado_id.empleado_id:
        search_employees(driver, empleado_id)
        time.sleep(1)
        logout(driver)
        fin = time.time()
        tiempo_transcurrido = fin - inicio

        print(f"La función tomó {tiempo_transcurrido} segundos en ejecutarse.")
    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")
    driver.quit()
    return {"status": "success"}