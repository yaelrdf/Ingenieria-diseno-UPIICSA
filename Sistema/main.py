from nicegui import ui, app
import database as db
from pages.dashboard import DashboardPage
from pages.pacientes import PacientesPage
from pages.citas import CitasPage
from pages.expedientes import ExpedientesPage
from pages.adeudos import AdeudosPage
from pages.odontograma import OdontogramaPage
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar base de datos
db.Database.initialize()

# Variable global para rastrear la página actual
current_page = None
page_container = None

def build_layout():
    """Build the layout structure with drawer and content area"""
    global page_container
    # Configurar tema y colores (se ejecuta al construir el layout, no en import)
    ui.colors(
        primary='#1976D2',
        secondary='#26A69A', 
        accent='#9C27B0',
        positive='#21BA45',
        negative='#C10015',
        info='#31CCEC',
        warning='#F2C037'
    )
    
    # Barra de navegación lateral
    with ui.left_drawer(bordered=True).classes('bg-blue-50') as drawer:
        ui.label('🦷 Clínica Dental').classes('text-h5 text-primary q-mb-md font-bold')
        
        menu_items = [
            ('dashboard', 'Dashboard', 'dashboard'),
            ('pacientes', 'Gestión de Pacientes', 'people'),
            ('citas', 'Citas', 'event'),
            ('expedientes', 'Expedientes', 'folder'),
            ('adeudos', 'Adeudos', 'attach_money'),
            ('odontograma', 'Odontograma', 'medical_services')
        ]
        
        for route, title, icon in menu_items:
            ui.button(title, 
                     on_click=lambda r=route: ui.navigate.to(f'/{r}'), 
                     icon=icon).props('flat').classes('w-full justify-start q-mb-1')
        
        # Pie de página con información
        ui.separator().classes('q-my-md')
        with ui.column().classes('w-full items-center'):
            ui.label('v1.0.0').classes('text-caption text-grey')
            ui.label('Sistema Dental').classes('text-caption text-grey')
    
    # Área de contenido principal
    with ui.column().classes('w-full'):
        # Barra superior
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('Sistema de Gestión Dental').classes('text-h4 text-weight-bold')
            
            with ui.row().classes('gap-2'):
                ui.button('Actualizar', icon='refresh', on_click=refresh_current_page)
        
        # Contenedor de la página actual
        page_container = ui.column().classes('w-full')

@ui.page('/')
def index():
    build_layout()
    render_dashboard()

@ui.page('/dashboard')
def dashboard():
    build_layout()
    render_dashboard()

@ui.page('/pacientes')
def pacientes():
    build_layout()
    render_pacientes()

@ui.page('/citas')
def citas():
    build_layout()
    render_citas()

@ui.page('/expedientes')
def expedientes(paciente_id: int | None = None):
    build_layout()
    render_expedientes(paciente_id)

@ui.page('/adeudos')
def adeudos():
    build_layout()
    render_adeudos()

@ui.page('/odontograma')
def odontograma():
    build_layout()
    render_odontograma()

def render_dashboard():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = DashboardPage()

def render_pacientes():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = PacientesPage()

def render_citas():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = CitasPage()

def render_expedientes(paciente_id: int | None = None):
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = ExpedientesPage(paciente_id=paciente_id)

def render_adeudos():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = AdeudosPage()

def render_odontograma():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = OdontogramaPage()

def refresh_current_page():
    """Recargar la página actual"""
    global current_page
    if current_page:
        if hasattr(current_page, 'refresh'):
            current_page.refresh()
        elif hasattr(current_page, 'cargar_datos'):
            current_page.cargar_datos()
        else:
            ui.notify('Recargando...', type='info')

# Manejar cierre de la aplicación
app.on_shutdown(db.Database.close_all)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Sistema de Gestión Dental",
        port=8080,
        reload=False,
        favicon="🦷",
        dark=False,
        show=False 
    )
    