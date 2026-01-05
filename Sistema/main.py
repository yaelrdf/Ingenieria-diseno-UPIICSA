from nicegui import ui, app
import database as db

ui.add_head_html('''
    <link href="https://fonts.googleapis.com/css2?family=Spicy+Rice&display=swap" rel="stylesheet">
    <style>
        .q-btn { text-transform: none !important; }
    </style>
''', shared=True)
from pages.dashboard import DashboardPage
from pages.pacientes import PacientesPage
from pages.citas import CitasPage
from pages.expedientes import ExpedientesPage
from pages.adeudos import AdeudosPage
from pages.odontograma import OdontogramaPage
from pages.medicos import MedicosPage
from pages.usuarios import UsuariosPage
from models.usuario_sistema import UsuarioSistema
import logging
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Inicializar base de datos
db.Database.initialize()

# Variable global para rastrear la página actual
current_page = None
page_container = None

def build_layout(active_route='dashboard'):
    """Build the layout structure with drawer and content area"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    
    user_data = app.storage.user.get('user', {})
    is_superadmin = user_data.get('es_superadmin', False)
    permisos = user_data.get('permisos', {})
    if isinstance(permisos, str):
        import json
        permisos = json.loads(permisos)
    allowed_menus = permisos.get('menus', [])

    global page_container
    # Configurar tema y colores para coincidir con el mockup
    ui.colors(
        primary='#9daaf2',
        secondary='#333333', 
        accent='#5c6bc0',
        positive='#21BA45',
        negative='#C10015',
        info='#31CCEC',
        warning='#F2C037'
    )
    
    # Barra de navegación lateral
    with ui.left_drawer(bordered=False).classes('bg-[#9daaf2] p-0 text-white overflow-y-auto overflow-x-hidden') as drawer:
        # Sección del Logo
        with ui.column().classes('w-full items-center py-4 gap-0'):
            try:
                ui.image('logo.png').classes('w-24 mb-2')
            except:
                ui.icon('pets', size='64px', color='white').classes('mb-2') # Fallback icon
            ui.label('Sonrisa perfecta').classes('text-h5 font-bold text-white').style('font-family: "Spicy Rice", cursive;')
        
        # Perfil de usuario
        with ui.row().classes('w-full items-center px-6 py-2 gap-4 bg-[#9daaf2]'):
             ui.avatar('img:https://cdn.pixabay.com/photo/2017/02/23/13/05/avatar-2092113_1280.png').classes('w-12 h-12 shadow-md')
             with ui.column().classes('gap-0 flex-grow'):
                 ui.label(user_data.get('nombre', 'Usuario')).classes('font-bold text-white')
                 ui.label(user_data.get('puesto', 'Puesto')).classes('text-caption text-blue-50')
             ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login')))\
                 .props('flat round color=white size=sm').tooltip('Cerrar sesión')
        
        ui.separator().classes('bg-white opacity-20 mx-6 mb-4')

        menu_items = [
            ('dashboard', 'Vista general', 'dashboard'),
            ('citas', 'Gestion de citas', 'event'),
            ('pacientes', 'Gestion de pacientes', 'people'),
            ('expedientes', 'Expedientes', 'folder_shared'),
            ('odontograma', 'Odontogramas', 'draw'),
            ('adeudos', 'Adeudos', 'payments'),
            ('medicos', 'Gestion de Medicos', 'medical_services'),
            ('usuarios', 'Usuarios', 'manage_accounts')
        ]
        
        for route, title, icon in menu_items:
            if not is_superadmin and route not in allowed_menus:
                continue
                
            is_active = active_route == route
            with ui.button(on_click=lambda r=route: ui.navigate.to(f'/{r}'))\
                .props('flat color=white no-caps')\
                .classes(f'w-full justify-start py-2 px-6 rounded-none {"bg-[#333333]" if is_active else "hover:bg-[#8c9ae5]"}'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon(icon, size='24px')
                    ui.label(title).classes('text-lg font-medium')
        
        ui.space()

        # Pie de página
        with ui.column().classes('w-full items-center pb-4'):
            ui.label('v1.0.0').classes('text-caption text-white opacity-60')
    
    # Área de contenido principal
    with ui.column().classes('w-full bg-white min-h-screen'):
        # Contenedor de la página actual
        page_container = ui.column().classes('w-full p-8')

@ui.page('/login')
def login_page():
    def try_login():
        query = "SELECT * FROM usuarios_sistema WHERE username = %s AND password = %s"
        user_data = db.fetch_one(query, (username.value, hash_password(password.value)))
        if user_data:
            # Columns: id, username, password, nombre, puesto, es_superadmin, permisos, medico_id, created_at
            columns = ['id', 'username', 'password', 'nombre', 'puesto', 'es_superadmin', 'permisos', 'medico_id', 'created_at']
            user_dict = dict(zip(columns, user_data))
            app.storage.user.update({
                'authenticated': True,
                'user': user_dict
            })
            ui.navigate.to('/')
        else:
            ui.notify('Usuario o contraseña incorrectos', color='negative')

    if app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return

    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('w-80 p-8 shadow-2xl'):
            with ui.column().classes('w-full items-center mb-6'):
                try:
                    ui.image('logo.png').classes('w-24 mb-2')
                except:
                    ui.icon('pets', size='64px', color='primary').classes('mb-2')
                ui.label('Sonrisa perfecta').classes('text-h5 font-bold text-primary').style('font-family: "Spicy Rice", cursive;')
            
            ui.label('Iniciar Sesión').classes('text-h6 text-center mb-4 text-grey-8')
            username = ui.input('Nombre de usuario').classes('w-full mb-2').on('keydown.enter', try_login)
            password = ui.input('Contraseña', password=True, password_toggle_button=True).classes('w-full mb-6').on('keydown.enter', try_login)
            ui.button('Entrar', on_click=try_login).classes('w-full py-2 text-lg rounded-lg').props('elevated color=primary')

@ui.page('/')
def index():
    build_layout('dashboard')
    render_dashboard()

@ui.page('/dashboard')
def dashboard():
    build_layout('dashboard')
    render_dashboard()

@ui.page('/pacientes')
def pacientes():
    build_layout('pacientes')
    render_pacientes()

@ui.page('/citas')
def citas():
    build_layout('citas')
    render_citas()

@ui.page('/expedientes')
def expedientes(paciente_id: int | None = None):
    build_layout('expedientes')
    render_expedientes(paciente_id)

@ui.page('/adeudos')
def adeudos():
    build_layout('adeudos')
    render_adeudos()

@ui.page('/odontograma')
def odontograma():
    build_layout('odontograma')
    render_odontograma()

@ui.page('/medicos')
def medicos():
    build_layout('medicos')
    render_medicos()

@ui.page('/usuarios')
def usuarios():
    build_layout('usuarios')
    render_usuarios()

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

def render_medicos():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = MedicosPage()

def render_usuarios():
    global current_page, page_container
    if page_container:
        page_container.clear()
        with page_container:
            current_page = UsuariosPage()

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
        title="Sonrisa perfecta",
        port=8080,
        reload=True,
        favicon="🐢",
        dark=False,
        show=False,
        storage_secret="sonrisa_perfecta_secret_key"
    )
    