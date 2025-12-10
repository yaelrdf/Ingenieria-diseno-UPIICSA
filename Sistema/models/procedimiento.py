from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Procedimiento:
    id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    costo: float = 0.0
    duracion_estimada: int = 30
    categoria: str = ""
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            costo=float(data.get('costo', 0)),
            duracion_estimada=data.get('duracion_estimada', 30),
            categoria=data.get('categoria', '')
        )

@dataclass
class ProcedimientoPaciente:
    id: Optional[int] = None
    paciente_id: Optional[int] = None
    procedimiento_id: Optional[int] = None
    cita_id: Optional[int] = None
    diente_numero: Optional[int] = None
    estado: str = "pendiente"
    fecha_realizacion: Optional[date] = None
    notas: str = ""
    costo: float = 0.0
    nombre_procedimiento: str = ""
    nombre_paciente: str = ""
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            paciente_id=data.get('paciente_id'),
            procedimiento_id=data.get('procedimiento_id'),
            cita_id=data.get('cita_id'),
            diente_numero=data.get('diente_numero'),
            estado=data.get('estado', 'pendiente'),
            fecha_realizacion=data.get('fecha_realizacion'),
            notas=data.get('notas', ''),
            costo=float(data.get('costo', 0)),
            nombre_procedimiento=data.get('nombre_procedimiento', ''),
            nombre_paciente=data.get('nombre_paciente', '')
        )