import pandas as pd
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from DB import engine, Base
from models import Empleado, DetalleContacto, DetalleSalario, DetalleAfiliacion

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(engine)

# Leer el archivo CSV
df = pd.read_csv("static/output_file.csv")

# Crear la sesión
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Procesar los datos e insertar en la base de datos
for index, row in df.iterrows():
    empleado = Empleado(
        tipo_cotizante=row['Tipo_Cotizante'],
        subtipo_cotizante=row['Subtipo_Cotizante'],
        subtipo_ugpp=row['Subtipo_UGPP'],
        tipo_identificacion=row['Tipo_Identificacion'],
        identificacion=row['Identificacion'],
        primer_nombre=row['Primer_Nombre'],
        segundo_nombre=row['Segundo_Nombre'],
        primer_apellido=row['Primer_Apellido'],
        segundo_apellido=row['Segundo_Apellido'],
        tipo_sexo=row['Tipo_Sexo'],
        cotizante_extranjero=row['Cotizante_Extranjero'],
        fecha_nacimiento=datetime.strptime(row['Fecha_Nacimiento'], '%m/%d/%Y'),
        edad=row['Edad'],
        fecha_expedicion=datetime.strptime(row['Fecha_Expedicion'], '%m/%d/%Y')
    )
    session.add(empleado)
    session.commit()

    detalle_contacto = DetalleContacto(
        empleado_id=empleado.id,
        numero_telefono=row['Numero_Telefono'],
        numero_celular=row['Numero_Celular'],
        direccion=row['Direccion'],
        ciudad_departamento=row['Ciudad_Departamento'],
        email=row['Email']
    )
    session.add(detalle_contacto)

    detalle_salario = DetalleSalario(
        empleado_id=empleado.id,
        salario_ibc=row['Salario_o_IBC'],
        vlr_administracion=row['Vlr_Administracion'],
        vlr_upc=row['Vlr_UPC'],
        estado=row['Estado'],
        valor_pila=row['Valor_PILA'],
        valor_otros=row['Valor_Otros'],
        valor_total=row['Valor_Total']
    )
    session.add(detalle_salario)

    detalle_afiliacion = DetalleAfiliacion(
        empleado_id=empleado.id,
        fecha_afiliacion=datetime.strptime(row['Fecha_Afiliacion'], '%m/%d/%Y'),
        afp=row['AFP'],
        afp_tarifa=row['AFPTarifa'],
        eps=row['EPS'],
        eps_tarifa=row['EPSTarifa'],
        arl=row['ARL'],
        arl_tarifa=row['ARLTarifa'],
        arl_nivel=row['ARL_Nivel'],
        planilla_n=row['Planilla_N'],
        ccf=row['CCF'],
        ccf_tarifa=row['CCFTarifa'],
        sena_tarifa=row['SENATarifa'],
        icbf_tarifa=row['ICBFTarifa']
    )
    session.add(detalle_afiliacion)

session.commit()
session.close()
