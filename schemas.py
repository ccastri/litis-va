from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal

class DetalleContactoSchema(BaseModel):
    id: Optional[int] = None
    empleado_id: int
    numero_telefono: Optional[str]
    numero_celular: str
    direccion: str
    ciudad_departamento: str
    email: Optional[str]
    observaciones: Optional[str]

    class Config:
        from_attributes = True

class DetalleSalarioSchema(BaseModel):
    id: Optional[int] = None
    empleado_id: int
    salario_ibc: Decimal
    mensajeria: str
    vlr_mensajeria: Decimal
    vlr_administracion: Decimal
    # vlr_upc: Optional[Decimal]
    estado: str
    valor_pila: Optional[Decimal]
    valor_total: Decimal

    class Config:
        from_attributes = True

class DetalleAfiliacionSchema(BaseModel):
    id: Optional[int] = None
    empleado_id: int
    fecha_afiliacion: date
    identificacion_asesor: Optional[int]
    nombre_asesor: Optional[str]
    afp: Optional[str]
    valor_comision: Optional[Decimal]
    afp_tarifa: Optional[Decimal]
    eps: str
    eps_tarifa: Decimal
    arl: str
    arl_tarifa: Decimal
    arl_nivel: int
    cod_ciiu: str
    planilla_n: Optional[str]
    ccf: str
    ciudad_ccf: str

    class Config:
        from_attributes = True

class EmpleadoSchema(BaseModel):
    id: Optional[int] = None
    tipo_identificacion: str
    identificacion: str
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: Optional[str]
    tipo_sexo: str
    cotizante_extranjero: bool
    fecha_nacimiento: date
    edad: int
    fecha_expedicion: date
    incapacidades: int
    detalles_contacto: Optional[DetalleContactoSchema] =[]
    detalles_salario: Optional[DetalleSalarioSchema] =[]
    detalles_afiliacion: Optional[DetalleAfiliacionSchema]  =[]

    class Config:
        from_attributes = True
