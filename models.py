from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.orm import sessionmaker
from DB import Base


class Afiliado(Base):
    __tablename__ = "afiliados"

    id = Column(Integer, primary_key=True)
    tipo_cotizante = Column(Integer)
    subtipo_cotizante = Column(Integer)
    subtipo_ugpp = Column(String(255))
    tipo_identificacion = Column(String(50))
    identificacion = Column(Integer)
    primer_nombre = Column(String(100))
    segundo_nombre = Column(String(100))
    primer_apellido = Column(String(100))
    segundo_apellido = Column(String(100))
    tipo_sexo = Column(String(10))
    salario_o_ibc = Column(Integer)
    cotizante_extranjero = Column(String(50))
    fecha_nacimiento = Column(Date)
    edad = Column(Integer)
    fecha_expedicion = Column(Date)
    numero_telefono = Column(String(20))
    numero_celular = Column(String(20))
    direccion = Column(String(255))
    ciudad_departamento = Column(String(100))
    email = Column(String(100))
    vlr_administracion = Column(Integer)
    vlr_upc = Column(Integer)
    identificacion_cotizante_upc = Column(Integer)
    excento_de_1607 = Column(String(50))
    centro_trabajo = Column(String(255))
    numero_folio = Column(Float)
    mensajeria = Column(String(100))
    vlr_mensajeria = Column(Integer)
    estado = Column(String(50))
    identificacion_asesor = Column(Float)
    nombre_asesor = Column(Float)
    valor_comision = Column(Integer)
    nit_empresa_servicio = Column(Float)
    razon_social_empresa_servicio = Column(Float)
    fecha_afiliacion = Column(Date)
    afp = Column(String(100))
    afp_tarifa = Column(Float)
    eps = Column(String(100))
    eps_tarifa = Column(Float)
    arl = Column(String(100))
    arl_tarifa = Column(Float)
    arl_nivel = Column(Integer)
    cod_ciiu = Column(Integer)
    planilla_n = Column(String(50))
    ccf = Column(String(100))
    ciudad_ccf = Column(String(100))
    ccf_tarifa = Column(Float)
    sena = Column(Float)
    sena_tarifa = Column(Float)
    icbf = Column(Float)
    icb_tarifa = Column(Float)
    valor_pila = Column(Integer)
    valor_otros = Column(Integer)
    valor_total = Column(Integer)
    incapacidades = Column(Integer)
    tipo_periodo = Column(String(50))
    modo_recaudo = Column(String(50))
    numero_nit = Column(Integer)
    razon_social = Column(String(255))
    observaciones = Column(Float)
    # Agrega más columnas aquí si las hay
