from nicegui import ui
from datetime import datetime, date, time, timedelta
import database as db
from models.cita import Cita
from components.paciente_selector import PacienteSelector

class CitaForm:
    def __init__(self, cita=None, on_save=None, on_cancel=None):
        self.cita = cita or Cita()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.paciente_id = self.cita.paciente_id
        self.paciente_nombre = self.cita.paciente_nombre
        if self.paciente_id and not self.paciente_nombre:
            self.cargar_nombre_paciente()
        self.create_form()
    
    def cargar_nombre_paciente(self):
        sql = "SELECT nombre || ' ' || apellidos FROM pacientes WHERE id = %s"
        res = db.fetch_one(sql, (self.paciente_id,))
        if res:
            self.paciente_nombre = res[0]

    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Nueva Cita' if not self.cita.id else 'Editar Cita').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4'):
                # Selector de paciente
                with ui.row().classes('w-full items-center gap-4'):
                    ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector).props('outline color=primary')
                    
                    self.paciente_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
                    with self.paciente_display:
                        ui.icon('person', color='primary')
                        self.label_paciente = ui.label(self.paciente_nombre or 'Sin seleccionar').classes('font-bold')
                    
                    self.paciente_display.set_visibility(self.paciente_id is not None)
                
                # Selector de doctor
                self.select_doctor = ui.select(
                    label='Doctor',
                    options=self.cargar_doctores(),
                    value=self.cita.doctor_id
                ).props('outlined').classes('w-full')
                
                # Fecha y hora
                with ui.row().classes('w-full gap-4'):
                    fecha_default = self.cita.fecha_hora.date() if self.cita.fecha_hora else date.today()
                    hora_default = self.cita.fecha_hora.time() if self.cita.fecha_hora else datetime.now().time()
                    
                    with ui.column().classes('w-1/2'):
                        ui.label('Fecha')
                        self.input_fecha = ui.date(value=fecha_default).props('outlined').classes('w-full')
                    with ui.column().classes('w-1/2'):
                        ui.label('Hora')
                        self.input_hora = ui.time(value=hora_default).props('outlined').classes('w-full')
                
                # Tipo de cita
                self.select_tipo = ui.select(
                    label='Tipo de Cita',
                    options={
                        'consulta': 'Consulta',
                        'limpieza': 'Limpieza Dental',
                        'procedimiento': 'Procedimiento',
                        'revision': 'Revisión',
                        'urgencia': 'Urgencia'
                    },
                    value=self.cita.tipo or 'consulta'
                ).props('outlined').classes('w-full')
                
                # Procedimiento
                self.input_procedimiento = ui.input(
                    'Procedimiento/Descripción',
                    value=self.cita.procedimiento or ''
                ).props('outlined').classes('w-full')
                
                # Duración
                self.select_duracion = ui.select(
                    label='Duración (minutos)',
                    options=[15, 30, 45, 60, 90, 120],
                    value=self.cita.duracion_minutos or 30
                ).props('outlined').classes('w-full')
                
                # Estado
                self.select_estado = ui.select(
                    label='Estado',
                    options={
                        'programada': 'Programada',
                        'en_curso': 'En Curso',
                        'completada': 'Completada',
                        'cancelada': 'Cancelada'
                    },
                    value=self.cita.estado or 'programada'
                ).props('outlined').classes('w-full')
                
                # Notas
                self.textarea_notas = ui.textarea(
                    'Notas',
                    value=self.cita.notas or ''
                ).props('outlined rows=3').classes('w-full')

                # Costo
                self.input_costo = ui.number(
                    'Costo de la Cita',
                    value=self.cita.costo or 0.0,
                    format='%.2f',
                    prefix='$'
                ).props('outlined').classes('w-full')
            
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
        query = "SELECT id, nombre FROM usuarios WHERE activo = true ORDER BY nombre"
        doctores = db.fetch_all(query)
        options = {None: 'Seleccionar Doctor'}
        for d in doctores:
            options[d[0]] = d[1]
        return options
    
    def guardar(self):
        # Combinar fecha y hora
        fecha_str = self.input_fecha.value
        hora_str = self.input_hora.value
        
        if not fecha_str or not hora_str:
            ui.notify('Seleccione fecha y hora válidas', type='warning')
            return
        
        try:
            # NiceGUI ui.date/ui.time returns strings, but we handle objects just in case
            if isinstance(fecha_str, str):
                fecha_obj = date.fromisoformat(fecha_str)
            else:
                fecha_obj = fecha_str
                
            if isinstance(hora_str, str):
                if len(hora_str) == 5: # HH:mm
                    hora_obj = time.fromisoformat(f"{hora_str}:00")
                else:
                    hora_obj = time.fromisoformat(hora_str)
            else:
                hora_obj = hora_str
                
            fecha_hora = datetime.combine(fecha_obj, hora_obj)
        except (ValueError, TypeError) as e:
            ui.notify(f'Formato de fecha o hora inválido: {e}', type='negative')
            return
        
        cita = Cita(
            id=self.cita.id,
            paciente_id=self.paciente_id,
            doctor_id=self.select_doctor.value,
            fecha_hora=fecha_hora,
            tipo=self.select_tipo.value,
            procedimiento=self.input_procedimiento.value,
            estado=self.select_estado.value,
            notas=self.textarea_notas.value,
            duracion_minutos=int(self.select_duracion.value),
            costo=float(self.input_costo.value or 0)
        )
        
        if self.on_save:
            self.on_save(cita)