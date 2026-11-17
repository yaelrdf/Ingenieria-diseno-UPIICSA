from datetime import date, datetime, time, timedelta

from nicegui import ui

import database as db
import servicios_citas as sc
from components.paciente_selector import PacienteSelector
from models.cita import Cita


class CitaForm:
    def __init__(self, cita=None, on_save=None, on_cancel=None):
        self.cita = cita or Cita()
        self.es_nueva = not self.cita.id
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.paciente_id = self.cita.paciente_id
        self.paciente_nombre = self.cita.paciente_nombre
        if self.paciente_id and not self.paciente_nombre:
            self.cargar_nombre_paciente()
        self.create_form()

    def cargar_nombre_paciente(self):
        res = db.fetch_one("SELECT nombre || ' ' || apellidos FROM pacientes WHERE id = %s", (self.paciente_id,))
        if res:
            self.paciente_nombre = res[0]

    @staticmethod
    def _hora_sugerida() -> datetime:
        """Siguiente bloque de 30 minutos a partir de ahora."""
        ahora = datetime.now().replace(second=0, microsecond=0)
        return ahora + timedelta(minutes=(30 - ahora.minute % 30) % 30 or 30)

    def create_form(self):
        sugerida = self._hora_sugerida()
        fecha_default = self.cita.fecha_hora.date() if self.cita.fecha_hora else sugerida.date()
        hora_default = (self.cita.fecha_hora or sugerida).strftime('%H:%M')
        # Solo se ofrecen fechas desde hoy (TC-56); al editar una cita pasada se conserva su fecha original
        minimo = min(date.today(), fecha_default).strftime('%Y/%m/%d')

        with ui.card().classes('w-full'):
            ui.label('Nueva Cita' if self.es_nueva else 'Editar Cita').classes('text-h6 mb-4')

            with ui.column().classes('w-full gap-4'):
                with ui.row().classes('w-full items-center gap-4'):
                    ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector).props('outline color=primary')
                    self.paciente_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
                    with self.paciente_display:
                        ui.icon('person', color='primary')
                        self.label_paciente = ui.label(self.paciente_nombre or 'Sin seleccionar').classes('font-bold')
                    self.paciente_display.set_visibility(self.paciente_id is not None)

                self.select_doctor = ui.select(
                    label='Doctor (opcional en primera vez)',
                    options=self.cargar_doctores(),
                    value=self.cita.doctor_id
                ).props('outlined').classes('w-full')

                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[290px]'):
                        ui.label('Fecha *')
                        self.input_fecha = ui.date(value=fecha_default) \
                            .props(f'''outlined :options="d => d >= '{minimo}'"''').classes('w-full')
                    with ui.column().classes('flex-1 min-w-[290px]'):
                        ui.label('Hora *')
                        self.input_hora = ui.time(value=hora_default).props('outlined').classes('w-full')

                self.select_tipo = ui.select(
                    label='Tipo de Cita *',
                    options=sc.TIPOS_CITA,
                    value=self.cita.tipo or 'consulta'
                ).props('outlined').classes('w-full')

                self.input_procedimiento = ui.input(
                    'Procedimiento/Descripción',
                    value=self.cita.procedimiento or ''
                ).props('outlined').classes('w-full')

                self.select_duracion = ui.select(
                    label='Duración (minutos)',
                    options=[15, 30, 45, 60, 90, 120],
                    value=self.cita.duracion_minutos or 30
                ).props('outlined').classes('w-full')

                # Una cita nueva siempre inicia como "Programada"; el estado solo se cambia al editar
                self.select_estado = None
                if not self.es_nueva:
                    self.select_estado = ui.select(
                        label='Estado',
                        options=sc.ESTADOS_CITA,
                        value=self.cita.estado or 'programada'
                    ).props('outlined').classes('w-full')

                self.textarea_notas = ui.textarea('Notas', value=self.cita.notas or '') \
                    .props('outlined rows=3').classes('w-full')

                self.input_costo = ui.number('Costo de la Cita', value=self.cita.costo or 0.0,
                                             format='%.2f', prefix='$', min=0) \
                    .props('outlined').classes('w-full')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.guardar, icon='save').props('flat color=primary')

    def abrir_selector(self):
        PacienteSelector(on_select=self.update_paciente).open()

    def update_paciente(self, pid, name):
        self.paciente_id = pid
        self.paciente_nombre = name
        self.label_paciente.set_text(name)
        self.paciente_display.set_visibility(True)

    def cargar_doctores(self):
        doctores = db.fetch_all('SELECT id, nombre FROM usuarios WHERE activo = true ORDER BY nombre')
        options = {None: 'Sin asignar'}
        for d in doctores:
            options[d[0]] = d[1]
        # Si la cita ya tiene un médico que fue desactivado, se muestra marcado para que se reasigne
        if self.cita.doctor_id and self.cita.doctor_id not in options:
            fila = db.fetch_one('SELECT nombre FROM usuarios WHERE id = %s', (self.cita.doctor_id,))
            if fila:
                options[self.cita.doctor_id] = f'{fila[0]} (inactivo)'
        return options

    def _leer_fecha_hora(self):
        fecha_val = self.input_fecha.value
        hora_val = self.input_hora.value
        if not fecha_val or not hora_val:
            return None
        fecha_obj = date.fromisoformat(fecha_val) if isinstance(fecha_val, str) else fecha_val
        if isinstance(hora_val, str):
            hora_obj = time.fromisoformat(hora_val[:5])
        else:
            hora_obj = hora_val
        return datetime.combine(fecha_obj, hora_obj).replace(second=0, microsecond=0)

    def guardar(self):
        try:
            fecha_hora = self._leer_fecha_hora()
        except (ValueError, TypeError):
            ui.notify('Formato de fecha u hora inválido', type='negative')
            return

        try:
            costo = float(self.input_costo.value or 0)
        except (ValueError, TypeError):
            ui.notify('El costo debe ser un número válido', type='warning')
            return

        cita = Cita(
            id=self.cita.id,
            paciente_id=self.paciente_id,
            doctor_id=self.select_doctor.value,
            fecha_hora=fecha_hora,
            tipo=self.select_tipo.value,
            procedimiento=(self.input_procedimiento.value or '').strip(),
            estado=self.select_estado.value if self.select_estado else 'programada',
            notas=self.textarea_notas.value,
            duracion_minutos=int(self.select_duracion.value or 30),
            costo=costo
        )

        error = sc.validar_cita(cita, None if self.es_nueva else self.cita)
        if error:
            ui.notify(error, type='warning', multi_line=True)
            return

        if self.on_save:
            self.on_save(cita)
