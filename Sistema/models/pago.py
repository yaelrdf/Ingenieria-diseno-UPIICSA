from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Pago:
    id: Optional[int] = None
    paciente_id: Optional[int] = None
    procedimiento_id: Optional[int] = None
    monto: float = 0.0
    metodo_pago: str = ""
    fecha_pago: Optional[date] = None
    concepto: str = ""
    notas: str = ""
    paciente_nombre: str = ""
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            paciente_id=data.get('paciente_id'),
            procedimiento_id=data.get('procedimiento_id'),
            monto=float(data.get('monto', 0)),
            metodo_pago=data.get('metodo_pago', ''),
            fecha_pago=data.get('fecha_pago'),
            concepto=data.get('concepto', ''),
            notas=data.get('notas', ''),
            paciente_nombre=data.get('paciente_nombre', '')
        )