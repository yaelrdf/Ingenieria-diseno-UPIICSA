from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
import json

@dataclass
class UsuarioSistema:
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    nombre: str = ""
    puesto: str = ""
    es_superadmin: bool = False
    permisos: Dict = field(default_factory=lambda: {"menus": ["dashboard"], "puede_eliminar": False})
    medico_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict):
        permisos = data.get('permisos')
        if isinstance(permisos, str):
            try:
                permisos = json.loads(permisos)
            except:
                permisos = {"menus": ["dashboard"], "puede_eliminar": False}
        
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            password=data.get('password', ''),
            nombre=data.get('nombre', ''),
            puesto=data.get('puesto', ''),
            es_superadmin=data.get('es_superadmin', False),
            permisos=permisos or {"menus": ["dashboard"], "puede_eliminar": False},
            medico_id=data.get('medico_id'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'nombre': self.nombre,
            'puesto': self.puesto,
            'es_superadmin': self.es_superadmin,
            'permisos': json.dumps(self.permisos),
            'medico_id': self.medico_id
        }
