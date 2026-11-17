import hashlib
import json
import logging
from pathlib import Path

from nicegui import app, ui

import database as db
from config import config
from pages.adeudos import AdeudosPage
from pages.citas import CitasPage
from pages.dashboard import DashboardPage
from pages.expedientes import ExpedientesPage
from pages.medicos import MedicosPage
from pages.odontograma import OdontogramaPage
from pages.pacientes import PacientesPage
from pages.usuarios import UsuariosPage

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
LOGO = str(BASE_DIR / 'logo.png')

# (ruta, título, ícono)
MENU_ITEMS = [
    ('dashboard', 'Vista general', 'dashboard'),
    ('citas', 'Gestion de citas', 'event'),
    ('pacientes', 'Gestion de pacientes', 'people'),
    ('expedientes', 'Expedientes', 'folder_shared'),
    ('odontograma', 'Odontogramas', 'draw'),
    ('adeudos', 'Adeudos', 'payments'),
    ('medicos', 'Gestion de Medicos', 'medical_services'),
    ('usuarios', 'Usuarios', 'manage_accounts'),
]

ui.add_head_html('''
    <link href="https://fonts.googleapis.com/css2?family=Spicy+Rice&display=swap" rel="stylesheet">
    <style>
        .q-btn { text-transform: none !important; }
    </style>
''', shared=True)

db.Database.initialize()
app.on_shutdown(db.Database.close_all)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Sesión y permisos
# ---------------------------------------------------------------------------

def obtener_usuario(user_id) -> dict | None:
    """Datos de la cuenta necesarios para la sesión (nunca incluye la contraseña)."""
    fila = db.fetch_one("""
        SELECT id, username, nombre, puesto, es_superadmin, permisos, medico_id
        FROM usuarios_sistema WHERE id = %s
    """, (user_id,))
    if not fila:
        return None
    permisos = fila[5]
    if isinstance(permisos, str):
        permisos = json.loads(permisos)
    return {
        'id': fila[0],
        'username': fila[1],
        'nombre': fila[2],
        'puesto': fila[3],
        'es_superadmin': bool(fila[4]),
        'permisos': permisos or {'menus': [], 'puede_eliminar': False},
        'medico_id': fila[6],
    }


def usuario_actual() -> dict | None:
    """Valida la sesión y recarga los permisos desde la BD en cada página."""
    if not app.storage.user.get('authenticated', False):
        return None
    user_id = (app.storage.user.get('user') or {}).get('id')
    user = obtener_usuario(user_id) if user_id else None
    if user is None:
        # La cuenta fue eliminada o la sesión es inválida
        app.storage.user.clear()
        return None
    app.storage.user['user'] = user
    return user


def menus_permitidos(user: dict) -> list[str]:
    if user.get('es_superadmin'):
        return [ruta for ruta, _, _ in MENU_ITEMS]
    permitidos = (user.get('permisos') or {}).get('menus', [])
    return [ruta for ruta, _, _ in MENU_ITEMS if ruta in permitidos]


def cerrar_sesion():
    app.storage.user.clear()
    ui.navigate.to('/login')


# ---------------------------------------------------------------------------
# Estructura visual
# ---------------------------------------------------------------------------

def construir_layout(user: dict, ruta_activa: str):
    """Dibuja el menú lateral y devuelve el contenedor del contenido de la página."""
    ui.colors(
        primary='#9daaf2',
        secondary='#333333',
        accent='#5c6bc0',
        positive='#21BA45',
        negative='#C10015',
        info='#31CCEC',
        warning='#F2C037'
    )
    permitidos = menus_permitidos(user)

    with ui.left_drawer(bordered=False).classes('bg-[#9daaf2] p-0 text-white overflow-y-auto overflow-x-hidden'):
        with ui.column().classes('w-full items-center py-4 gap-0'):
            ui.image(LOGO).classes('w-24 mb-2')
            ui.label('Sonrisa perfecta').classes('text-h5 font-bold text-white').style('font-family: "Spicy Rice", cursive;')

        with ui.row().classes('w-full items-center px-6 py-2 gap-4 bg-[#9daaf2] no-wrap'):
            ui.avatar(icon='person', color='white', text_color='primary').classes('shadow-md')
            with ui.column().classes('gap-0 flex-grow'):
                ui.label(user.get('nombre') or 'Usuario').classes('font-bold text-white')
                ui.label(user.get('puesto') or '').classes('text-caption text-blue-50')
            ui.button(icon='logout', on_click=cerrar_sesion).props('flat round color=white size=sm').tooltip('Cerrar sesión')

        ui.separator().classes('bg-white opacity-20 mx-6 mb-4')

        for ruta, titulo, icono in MENU_ITEMS:
            if ruta not in permitidos:
                continue
            activo = ruta == ruta_activa
            with ui.button(on_click=lambda r=ruta: ui.navigate.to(f'/{r}')) \
                    .props('flat color=white no-caps') \
                    .classes(f'w-full justify-start py-2 px-6 rounded-none {"bg-[#333333]" if activo else "hover:bg-[#8c9ae5]"}'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon(icono, size='24px')
                    ui.label(titulo).classes('text-lg font-medium')

        ui.space()
        with ui.column().classes('w-full items-center pb-4'):
            ui.label(f'v{config.APP_VERSION}').classes('text-caption text-white opacity-60')

    with ui.column().classes('w-full bg-white min-h-screen'):
        return ui.column().classes('w-full p-8')


def mensaje_bloqueo(icono: str, titulo: str, detalle: str):
    with ui.column().classes('w-full items-center mt-16 gap-2 text-grey-7'):
        ui.icon(icono, size='64px', color='grey-5')
        ui.label(titulo).classes('text-h5')
        ui.label(detalle).classes('text-body1')


def mostrar_pagina(ruta: str, crear_pagina):
    """Punto de entrada común: exige sesión y permiso sobre el módulo antes de dibujarlo."""
    user = usuario_actual()
    if user is None:
        ui.navigate.to('/login')
        return
    contenido = construir_layout(user, ruta)
    with contenido:
        if ruta in menus_permitidos(user):
            crear_pagina()
        else:
            mensaje_bloqueo('lock', 'Acceso restringido',
                            'Su cuenta no tiene permiso para acceder a este módulo.')


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@ui.page('/login')
def login_page():
    if usuario_actual():
        ui.navigate.to('/')
        return

    def try_login():
        nombre_usuario = (username.value or '').strip()
        clave = password.value or ''
        if not nombre_usuario and not clave:
            ui.notify('Ingrese usuario y contraseña', type='warning')
            return
        if not nombre_usuario:
            ui.notify('El usuario es obligatorio', type='warning')
            return
        if not clave:
            ui.notify('La contraseña es obligatoria', type='warning')
            return

        fila = db.fetch_one('SELECT id FROM usuarios_sistema WHERE username = %s AND password = %s',
                            (nombre_usuario, hash_password(clave)))
        if not fila:
            ui.notify('Usuario o contraseña incorrectos', color='negative')
            return
        app.storage.user.update({'authenticated': True, 'user': obtener_usuario(fila[0])})
        ui.navigate.to('/')

    with ui.column().classes('absolute-center items-center'):
        with ui.card().classes('w-80 p-8 shadow-2xl'):
            with ui.column().classes('w-full items-center mb-6'):
                ui.image(LOGO).classes('w-24 mb-2')
                ui.label('Sonrisa perfecta').classes('text-h5 font-bold text-primary').style('font-family: "Spicy Rice", cursive;')

            ui.label('Iniciar Sesión').classes('text-h6 text-center mb-4 text-grey-8')
            username = ui.input('Nombre de usuario').classes('w-full mb-2').on('keydown.enter', try_login)
            password = ui.input('Contraseña', password=True, password_toggle_button=True).classes('w-full mb-6').on('keydown.enter', try_login)
            ui.button('Entrar', on_click=try_login).classes('w-full py-2 text-lg rounded-lg').props('elevated color=primary')


@ui.page('/')
def index():
    user = usuario_actual()
    if user is None:
        ui.navigate.to('/login')
        return
    permitidos = menus_permitidos(user)
    if 'dashboard' in permitidos:
        mostrar_pagina('dashboard', DashboardPage)
    elif permitidos:
        ui.navigate.to(f'/{permitidos[0]}')
    else:
        with construir_layout(user, ''):
            mensaje_bloqueo('info', 'Sin módulos asignados',
                            'Solicite a un administrador que le asigne permisos de acceso.')


@ui.page('/dashboard')
def dashboard():
    mostrar_pagina('dashboard', DashboardPage)


@ui.page('/pacientes')
def pacientes():
    mostrar_pagina('pacientes', PacientesPage)


@ui.page('/citas')
def citas():
    mostrar_pagina('citas', CitasPage)


@ui.page('/expedientes')
def expedientes(paciente_id: int | None = None):
    mostrar_pagina('expedientes', lambda: ExpedientesPage(paciente_id=paciente_id))


@ui.page('/adeudos')
def adeudos():
    mostrar_pagina('adeudos', AdeudosPage)


@ui.page('/odontograma')
def odontograma():
    mostrar_pagina('odontograma', OdontogramaPage)


@ui.page('/medicos')
def medicos():
    mostrar_pagina('medicos', MedicosPage)


@ui.page('/usuarios')
def usuarios():
    mostrar_pagina('usuarios', UsuariosPage)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title=config.APP_TITLE,
        host='0.0.0.0',
        port=config.APP_PORT,
        reload=False,
        favicon=LOGO,
        dark=False,
        show=False,
        storage_secret=config.STORAGE_SECRET,
    )
