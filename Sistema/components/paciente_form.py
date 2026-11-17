from datetime import date

from nicegui import ui

import validaciones as val
from models.paciente import Paciente


class PacienteForm:
    def __init__(self, paciente=None, on_save=None, on_cancel=None):
        self.paciente = paciente or Paciente()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()
        self.calcular_edad()

    def _fecha_nacimiento(self):
        try:
            return val.parse_fecha(self.fecha_nacimiento.value)
        except (ValueError, TypeError):
            return None

    def calcular_edad(self, e=None):
        fecha_nac = self._fecha_nacimiento()
        if not fecha_nac or fecha_nac > date.today():
            self.edad_display.set_text('')
            return
        self.edad_display.set_text(str(val.calcular_edad(fecha_nac)))

    def create_form(self):
        hoy = date.today().strftime('%Y/%m/%d')
        with ui.card().classes('w-full'):
            ui.label('Datos del Paciente').classes('text-h6')

            with ui.row().classes('w-full'):
                # Validación en tiempo real: 18 caracteres alfanuméricos (TC-25, TC-27, TC-86)
                self.curp = ui.input('CURP *', value=self.paciente.curp, validation=val.validar_curp) \
                    .props('outlined maxlength=18 counter input-style="text-transform: uppercase"') \
                    .classes('w-full')

            with ui.row().classes('w-full no-wrap'):
                self.nombre = ui.input('Nombre *', value=self.paciente.nombre,
                                       validation=val.validar_obligatorio('El nombre')) \
                    .props('outlined').classes('flex-1 min-w-0')
                self.apellidos = ui.input('Apellidos *', value=self.paciente.apellidos,
                                          validation=val.validar_obligatorio('Los apellidos')) \
                    .props('outlined').classes('flex-1 min-w-0')

            with ui.row().classes('w-full no-wrap'):
                with ui.column().classes('flex-1 min-w-0'):
                    ui.label('Fecha de Nacimiento *')
                    self.fecha_nacimiento = ui.date(value=self.paciente.fecha_nacimiento,
                                                    on_change=self.calcular_edad) \
                        .props(f'''outlined :options="d => d <= '{hoy}'"''').classes('w-full')
                with ui.column().classes('flex-1 min-w-0 gap-0'):
                    ui.label('Edad').classes('text-gray-600 text-caption')
                    self.edad_display = ui.label('').classes('text-body1')

            with ui.row().classes('w-full no-wrap'):
                self.genero = ui.select(['Masculino', 'Femenino', 'Otro'],
                                        value=self.paciente.genero if self.paciente.genero in ['Masculino', 'Femenino', 'Otro'] else None,
                                        label='Género').props('outlined clearable').classes('flex-1 min-w-0')
                self.telefono = ui.input('Teléfono', value=self.paciente.telefono or '',
                                         validation=val.validar_telefono) \
                    .props('outlined maxlength=10').classes('flex-1 min-w-0')

            self.email = ui.input('Email', value=self.paciente.email or '', validation=val.validar_email) \
                .props('outlined').classes('w-full')
            self.direccion = ui.input('Dirección', value=self.paciente.direccion or '').props('outlined').classes('w-full')

            with ui.expansion('Historial Médico', icon='medical_services').classes('w-full'):
                self.alergias = ui.textarea('Alergias', value=self.paciente.alergias).props('outlined').classes('w-full')
                self.enfermedades = ui.textarea('Enfermedades Crónicas', value=self.paciente.enfermedades_cronicas).props('outlined').classes('w-full')
                self.medicamentos = ui.textarea('Medicamentos', value=self.paciente.medicamentos).props('outlined').classes('w-full')
                self.observaciones = ui.textarea('Observaciones', value=self.paciente.observaciones).props('outlined').classes('w-full')

            ui.label('* Campos obligatorios').classes('text-caption text-grey-7')
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.save, icon='save').props('flat color=primary')

    def save(self):
        campos = [self.curp, self.nombre, self.apellidos, self.telefono, self.email]
        resultados = [campo.validate() for campo in campos]  # se validan todos para marcar cada error
        if not all(resultados):
            ui.notify('Corrija los campos marcados en rojo antes de guardar', type='warning')
            return

        if not self.fecha_nacimiento.value:
            ui.notify('La fecha de nacimiento es obligatoria', type='warning')
            return
        fecha_nac = self._fecha_nacimiento()
        if fecha_nac is None:
            ui.notify('La fecha de nacimiento no es válida', type='warning')
            return
        if fecha_nac > date.today():
            ui.notify('La fecha de nacimiento no puede ser futura', type='warning')
            return

        paciente = Paciente(
            id=self.paciente.id,
            curp=val.texto(self.curp.value).upper(),
            nombre=val.texto(self.nombre.value),
            apellidos=val.texto(self.apellidos.value),
            fecha_nacimiento=fecha_nac,
            edad=val.calcular_edad(fecha_nac),
            genero=self.genero.value,
            telefono=val.texto(self.telefono.value) or None,
            email=val.texto(self.email.value) or None,
            direccion=val.texto(self.direccion.value) or None,
            alergias=self.alergias.value,
            enfermedades_cronicas=self.enfermedades.value,
            medicamentos=self.medicamentos.value,
            observaciones=self.observaciones.value
        )

        if self.on_save:
            self.on_save(paciente)
