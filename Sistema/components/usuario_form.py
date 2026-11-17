from nicegui import ui

import validaciones as val
from models.usuario import Usuario


class UsuarioForm:
    """Formulario de alta y edición de médicos."""

    def __init__(self, usuario=None, on_save=None, on_cancel=None):
        self.usuario = usuario or Usuario()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()

    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Datos del Médico').classes('text-h6 mb-4')

            with ui.column().classes('w-full gap-4'):
                self.nombre = ui.input('Nombre Completo *', value=self.usuario.nombre,
                                       validation=val.validar_obligatorio('El nombre')) \
                    .props('outlined').classes('w-full')
                # Validación de formato con dominio (TC-43)
                self.email = ui.input('Email *', value=self.usuario.email,
                                      validation=lambda v: val.validar_email(v, obligatorio=True)) \
                    .props('outlined').classes('w-full')
                self.telefono = ui.input('Teléfono', value=self.usuario.telefono or '',
                                         validation=val.validar_telefono) \
                    .props('outlined maxlength=10').classes('w-full')
                self.especialidad = ui.input('Especialidad', value=self.usuario.especialidad or '') \
                    .props('outlined').classes('w-full')

                with ui.row().classes('w-full items-center'):
                    ui.label('Estado:')
                    self.activo = ui.switch('Activo', value=self.usuario.activo)

            ui.label('* Campos obligatorios').classes('text-caption text-grey-7')
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.save, icon='save').props('flat color=primary')

    def save(self):
        resultados = [campo.validate() for campo in (self.nombre, self.email, self.telefono)]
        if not all(resultados):
            ui.notify('Corrija los campos marcados en rojo antes de guardar', type='warning')
            return

        usuario = Usuario(
            id=self.usuario.id,
            nombre=val.texto(self.nombre.value),
            email=val.texto(self.email.value).lower(),
            telefono=val.texto(self.telefono.value) or None,
            especialidad=val.texto(self.especialidad.value) or None,
            activo=self.activo.value
        )

        if self.on_save:
            self.on_save(usuario)
