from nicegui import ui
from models.usuario_sistema import UsuarioSistema
import database as db
import hashlib

class UsuarioSistemaForm:
    def __init__(self, usuario=None, on_save=None, on_cancel=None):
        self.usuario = usuario or UsuarioSistema()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()

    def create_form(self):
        # Fetch doctors for the selector
        medicos_data = db.fetch_all("SELECT id, nombre FROM usuarios WHERE activo = true ORDER BY nombre")
        medicos_options = {None: 'Ninguno'}
        for m in medicos_data:
            medicos_options[m[0]] = m[1]

        with ui.card().classes('w-full'):
            ui.label('Datos de Cuenta de Usuario').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4'):
                self.username = ui.input('Nombre de Usuario', value=self.usuario.username).props('outlined').classes('w-full')
                if self.usuario.username == 'admin':
                    self.username.props('readonly')
                
                self.password = ui.input('Contraseña', password=True, password_toggle_button=True).props('outlined').classes('w-full')
                if self.usuario.id:
                    self.password.placeholder = "Dejar en blanco para no cambiar"
                
                self.nombre = ui.input('Nombre Real', value=self.usuario.nombre).props('outlined').classes('w-full')
                self.puesto = ui.input('Puesto/Cargo', value=self.usuario.puesto).props('outlined').classes('w-full')
                
                self.medico_id = ui.select(medicos_options, label='Vincular con Médico', value=self.usuario.medico_id).props('outlined').classes('w-full')
                
                ui.label('Permisos de Acceso (Menús)').classes('text-subtitle1 mt-2')
                menus = [
                    ('dashboard', 'Vista general'),
                    ('citas', 'Gestion de citas'),
                    ('pacientes', 'Gestion de pacientes'),
                    ('expedientes', 'Expedientes'),
                    ('odontograma', 'Odontogramas'),
                    ('adeudos', 'Adeudos'),
                    ('medicos', 'Gestion de Medicos'),
                    ('usuarios', 'Usuarios')
                ]
                
                self.menu_checks = {}
                with ui.grid(columns=2).classes('w-full'):
                    for route, label in menus:
                        self.menu_checks[route] = ui.checkbox(label, value=route in self.usuario.permisos.get('menus', []))
                
                ui.label('ZONA DE PELIGRO').classes('text-subtitle1 text-red font-bold mt-4')
                with ui.column().classes('w-full border border-red-200 p-3 rounded bg-red-50'):
                    self.es_superadmin = ui.checkbox('Es Super Admin', value=self.usuario.es_superadmin)
                    if self.usuario.username == 'admin':
                        self.es_superadmin.disable()
                    
                    self.puede_eliminar = ui.checkbox('Puede Eliminar Items (Global)', value=self.usuario.permisos.get('puede_eliminar', False))
                    if self.usuario.username == 'admin':
                        self.puede_eliminar.disable()

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.save, icon='save').props('flat color=primary')

    def save(self):
        if not self.username.value or not self.nombre.value:
            ui.notify('Nombre de usuario y nombre real son obligatorios', type='warning')
            return
        
        if not self.usuario.id and not self.password.value:
            ui.notify('La contraseña es obligatoria para nuevos usuarios', type='warning')
            return

        permisos = {
            'menus': [route for route, check in self.menu_checks.items() if check.value],
            'puede_eliminar': self.puede_eliminar.value
        }

        # Validar si el username ya existe (si es nuevo)
        if not self.usuario.id:
            existe = db.fetch_one("SELECT id FROM usuarios_sistema WHERE username = %s", (self.username.value,))
            if existe:
                ui.notify('El nombre de usuario ya existe', type='negative')
                return

        usuario_dict = {
            'id': self.usuario.id,
            'username': self.username.value,
            'nombre': self.nombre.value,
            'puesto': self.puesto.value,
            'es_superadmin': self.es_superadmin.value,
            'permisos': permisos,
            'medico_id': self.medico_id.value
        }
        
        if self.password.value:
            usuario_dict['password'] = hashlib.sha256(self.password.value.encode()).hexdigest()
        else:
            usuario_dict['password'] = self.usuario.password

        usuario = UsuarioSistema.from_dict(usuario_dict)
        
        if self.on_save:
            self.on_save(usuario)
