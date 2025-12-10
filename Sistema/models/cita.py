from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Cita:
    id: Optional[int] = None
    paciente_id: Optional[int] = None
    doctor_id: Optional[int] = None
    fecha_hora: Optional[datetime] = None
    tipo: str = ""
    procedimiento: str = ""
    estado: str = "programada"
    notas: str = ""
    duracion_minutos: int = 30
    paciente_nombre: str = ""
    doctor_nombre: str = ""