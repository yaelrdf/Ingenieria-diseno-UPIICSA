# Exportar todas las páginas
from .dashboard import DashboardPage
from .pacientes import PacientesPage
from .citas import CitasPage
from .expedientes import ExpedientesPage
from .adeudos import AdeudosPage
from .odontograma import OdontogramaPage

__all__ = [
    'DashboardPage',
    'PacientesPage', 
    'CitasPage',
    'ExpedientesPage',
    'AdeudosPage',
    'OdontogramaPage'
]