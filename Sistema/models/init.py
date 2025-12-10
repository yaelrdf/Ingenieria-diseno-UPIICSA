# Exportar todos los modelos
from .paciente import Paciente
from .cita import Cita
from .procedimiento import Procedimiento, ProcedimientoPaciente
from .pago import Pago

__all__ = ['Paciente', 'Cita', 'Procedimiento', 'ProcedimientoPaciente', 'Pago']