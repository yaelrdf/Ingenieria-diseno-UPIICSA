from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Paciente:
    id: Optional[int] = None
    curp: str = ""
    nombre: str = ""
    apellidos: str = ""
    fecha_nacimiento: Optional[date] = None
    edad: Optional[int] = None
    genero: str = ""
    telefono: str = ""
    email: str = ""
    direccion: str = ""
    alergias: str = ""
    enfermedades_cronicas: str = ""
    medicamentos: str = ""
    observaciones: str = ""
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            curp=data.get('curp', ''),
            nombre=data.get('nombre', ''),
            apellidos=data.get('apellidos', ''),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            edad=data.get('edad'),
            genero=data.get('genero', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            direccion=data.get('direccion', ''),
            alergias=data.get('alergias', ''),
            enfermedades_cronicas=data.get('enfermedades_cronicas', ''),
            medicamentos=data.get('medicamentos', ''),
            observaciones=data.get('observaciones', '')
        )
    
    def to_dict(self):
        return {
            'curp': self.curp,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'fecha_nacimiento': self.fecha_nacimiento,
            'edad': self.edad,
            'genero': self.genero,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'alergias': self.alergias,
            'enfermedades_cronicas': self.enfermedades_cronicas,
            'medicamentos': self.medicamentos,
            'observaciones': self.observaciones
        }