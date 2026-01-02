from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Usuario:
    id: Optional[int] = None
    nombre: str = ""
    email: str = ""
    telefono: str = ""
    especialidad: str = ""
    activo: bool = True
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            especialidad=data.get('especialidad', ''),
            activo=data.get('activo', True),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'especialidad': self.especialidad,
            'activo': self.activo
        }
