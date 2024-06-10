from sqlalchemy import Column, Integer, String, Date, Boolean, DECIMAL, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from DB import Base

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    tipo_identificacion = Column(String, nullable=False)
    identificacion = Column(String, nullable=False, unique=True)
    primer_nombre = Column(String, nullable=False)
    segundo_nombre = Column(String)
    primer_apellido = Column(String, nullable=False)
    segundo_apellido = Column(String, nullable=True)
    tipo_sexo = Column(String(1), nullable=False)
    cotizante_extranjero = Column(Boolean, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    edad = Column(Integer, nullable=False)
    fecha_expedicion = Column(Date, nullable=False)
    incapacidades = Column(Integer, nullable=False)
    detalles_contacto = relationship("DetalleContacto", back_populates="empleado", uselist=False)
    detalles_salario = relationship("DetalleSalario", back_populates="empleado", uselist=False)
    detalles_afiliacion = relationship("DetalleAfiliacion", back_populates="empleado")
    detalles_nomina = relationship("DetalleNomina", back_populates="empleado")
    mensajes = relationship("Message", back_populates="empleado")

class DetalleContacto(Base):
    __tablename__ = "detalles_contacto"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=False)
    numero_telefono = Column(String, nullable=True)
    numero_celular = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    ciudad_departamento = Column(String, nullable=False)
    email = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)

    empleado = relationship("Empleado", back_populates="detalles_contacto")

class DetalleSalario(Base):
    __tablename__ = "detalles_salario"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=False)
    salario_ibc = Column(DECIMAL(10,2), nullable=False)
    mensajeria = Column(String(1), nullable=False)
    vlr_mensajeria = Column(DECIMAL(10,2), nullable=False)
    vlr_administracion = Column(DECIMAL(10,2), nullable=False)
    estado = Column(String, nullable=False)
    valor_pila = Column(DECIMAL(10,2), nullable=True)
    valor_total = Column(DECIMAL(10,2), nullable=False)

    empleado = relationship("Empleado", back_populates="detalles_salario")

class DetalleAfiliacion(Base):
    __tablename__ = "detalles_afiliacion"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=False)
    fecha_afiliacion = Column(Date, nullable=False)
    identificacion_asesor = Column(Integer)
    nombre_asesor = Column(String)
    afp = Column(String, nullable=True)
    valor_comision = Column(Numeric(10,2), nullable=True)
    afp_tarifa = Column(Numeric(5,4), nullable=True)
    eps = Column(String, nullable=False)
    eps_tarifa = Column(Numeric(5,4), nullable=False)
    arl = Column(String, nullable=False)
    arl_tarifa = Column(Numeric(5,4), nullable=False)
    arl_nivel = Column(Integer, nullable=False)
    cod_ciiu = Column(String, nullable=False)
    planilla_n = Column(String, nullable=True)
    ccf = Column(String, nullable=False)
    ciudad_ccf = Column(String, nullable=False)

    empleado = relationship("Empleado", back_populates="detalles_afiliacion")

class DetalleNomina(Base):
    __tablename__ = "detalles_nomina"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    salario_base = Column(DECIMAL(10,2), nullable=False)
    total_aportes = Column(DECIMAL(10,2), nullable=False)
    total_descuentos = Column(DECIMAL(10,2), nullable=False)
    total_horas_extras = Column(DECIMAL(10,2), nullable=False)
    total_comisiones = Column(DECIMAL(10,2), nullable=False)
    total_pagado = Column(DECIMAL(10,2), nullable=False)

    empleado = relationship("Empleado", back_populates="detalles_nomina")
    aportes = relationship("AporteLey", back_populates="detalle_nomina")
    descuentos = relationship("Descuento", back_populates="detalle_nomina")
    horas_extras = relationship("HoraExtra", back_populates="detalle_nomina")
    comisiones = relationship("Comision", back_populates="detalle_nomina")

class AporteLey(Base):
    __tablename__ = "aportes_ley"

    id = Column(Integer, primary_key=True, index=True)
    detalle_nomina_id = Column(Integer, ForeignKey('detalles_nomina.id'), nullable=False)
    tipo_aporte = Column(String, nullable=False)
    valor = Column(DECIMAL(10,2), nullable=False)

    detalle_nomina = relationship("DetalleNomina", back_populates="aportes")

class Descuento(Base):
    __tablename__ = "descuentos"

    id = Column(Integer, primary_key=True, index=True)
    detalle_nomina_id = Column(Integer, ForeignKey('detalles_nomina.id'), nullable=False)
    tipo_descuento = Column(String, nullable=False)
    valor = Column(DECIMAL(10,2), nullable=False)

    detalle_nomina = relationship("DetalleNomina", back_populates="descuentos")

class HoraExtra(Base):
    __tablename__ = "horas_extras"

    id = Column(Integer, primary_key=True, index=True)
    detalle_nomina_id = Column(Integer, ForeignKey('detalles_nomina.id'), nullable=False)
    tipo_hora_extra = Column(String, nullable=False)
    horas = Column(DECIMAL(10,2), nullable=False)
    valor = Column(DECIMAL(10,2), nullable=False)

    detalle_nomina = relationship("DetalleNomina", back_populates="horas_extras")

class Comision(Base):
    __tablename__ = "comisiones"

    id = Column(Integer, primary_key=True, index=True)
    detalle_nomina_id = Column(Integer, ForeignKey('detalles_nomina.id'), nullable=False)
    concepto = Column(String, nullable=False)
    valor = Column(DECIMAL(10,2), nullable=False)

    detalle_nomina = relationship("DetalleNomina", back_populates="comisiones")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('empleados.id'), nullable=False)
    recipient = Column(String, default="chatbot", nullable=False)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    empleado = relationship("Empleado", back_populates="mensajes")

class MensajePredeterminado(Base):
    __tablename__ = "mensajes_predeterminados"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    contexto = Column(Text, nullable=True)
    respuesta_predeterminada = Column(Text, nullable=False)
