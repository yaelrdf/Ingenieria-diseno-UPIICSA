from nicegui import ui
from models.usuario import Usuario

class UsuarioForm:
    def __init__(self, usuario=None, on_save=None, on_cancel=None):
        self.usuario = usuario or Usuario()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()
    
    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Datos del Médico').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4'):
                self.nombre = ui.input('Nombre Completo', value=self.usuario.nombre).props('outlined').classes('w-full')
                self.email = ui.input('Email', value=self.usuario.email).props('outlined').classes('w-full')
                self.telefono = ui.input('Teléfono', value=self.usuario.telefono).props('outlined').classes('w-full')
                self.especialidad = ui.input('Especialidad', value=self.usuario.especialidad).props('outlined').classes('w-full')
                
                with ui.row().classes('w-full items-center'):
                    ui.label('Estado:')
                    self.activo = ui.switch('Activo', value=self.usuario.activo)
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.save, icon='save').props('flat color=primary')
    
    def save(self):
        if not self.nombre.value or not self.email.value:
            ui.notify('Por favor complete los campos obligatorios: Nombre y Email', type='warning')
            return
            
        usuario = Usuario(
            id=self.usuario.id,
            nombre=self.nombre.value,
            email=self.email.value,
            telefono=self.telefono.value,
            especialidad=self.especialidad.value,
            activo=self.activo.value
        )
        
        if self.on_save:
            self.on_save(usuario)
