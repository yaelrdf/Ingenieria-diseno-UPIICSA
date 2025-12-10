from nicegui import ui
from datetime import datetime, date, timedelta
import database as db
from models.cita import Cita

class CitaForm:
    def __init__(self, cita=None, on_save=None, on_cancel=None):
        self.cita = cita or Cita()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()
    
    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Nueva Cita' if not self.cita.id else 'Editar Cita').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4'):
                # Selector de paciente
                self.select_paciente = ui.select(
                    label='Paciente',
                    options=self.cargar_pacientes(),
                    value=self.cita.paciente_id
                ).props('outlined clearable').classes('w-full')
                
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
                    options=[
                        ('consulta', 'Consulta'),
                        ('limpieza', 'Limpieza Dental'),
                        ('procedimiento', 'Procedimiento'),
                        ('revision', 'Revisión'),
                        ('urgencia', 'Urgencia')
                    ],
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
                    options=[
                        ('programada', 'Programada'),
                        ('en_curso', 'En Curso'),
                        ('completada', 'Completada'),
                        ('cancelada', 'Cancelada')
                    ],
                    value=self.cita.estado or 'programada'
                ).props('outlined').classes('w-full')
                
                # Notas
                self.textarea_notas = ui.textarea(
                    'Notas',
                    value=self.cita.notas or ''
                ).props('outlined rows=3').classes('w-full')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.guardar, icon='save').props('flat color=primary')
    
    def cargar_pacientes(self):
        query = "SELECT id, nombre || ' ' || apellidos as nombre FROM pacientes ORDER BY nombre"
        pacientes = db.fetch_all(query)
        return {p[0]: p[1] for p in pacientes}
    
    def cargar_doctores(self):
        query = "SELECT id, nombre FROM usuarios WHERE activo = true ORDER BY nombre"
        doctores = db.fetch_all(query)
        return {d[0]: d[1] for d in doctores}
    
    def guardar(self):
        # Combinar fecha y hora
        fecha = self.input_fecha.value
        hora = self.input_hora.value
        
        if not fecha or not hora:
            ui.notify('Seleccione fecha y hora válidas', type='warning')
            return
        
        fecha_hora = datetime.combine(fecha, hora)
        
        cita = Cita(
            id=self.cita.id,
            paciente_id=self.select_paciente.value,
            doctor_id=self.select_doctor.value,
            fecha_hora=fecha_hora,
            tipo=self.select_tipo.value,
            procedimiento=self.input_procedimiento.value,
            estado=self.select_estado.value,
            notas=self.textarea_notas.value,
            duracion_minutos=int(self.select_duracion.value)
        )
        
        if self.on_save:
            self.on_save(cita)