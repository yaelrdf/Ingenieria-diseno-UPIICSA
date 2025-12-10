from nicegui import ui
from datetime import date
from models.paciente import Paciente

class PacienteForm:
    def __init__(self, paciente=None, on_save=None, on_cancel=None):
        self.paciente = paciente or Paciente()
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()
    
    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Datos del Paciente').classes('text-h6')
            
            with ui.row().classes('w-full'):
                self.curp = ui.input('CURP', value=self.paciente.curp).props('outlined').classes('w-full')
            
            with ui.row().classes('w-full'):
                self.nombre = ui.input('Nombre', value=self.paciente.nombre).props('outlined').classes('w-1/2')
                self.apellidos = ui.input('Apellidos', value=self.paciente.apellidos).props('outlined').classes('w-1/2')
            
            with ui.row().classes('w-full'):
                self.fecha_nacimiento = ui.date(value=self.paciente.fecha_nacimiento, label='Fecha de Nacimiento').props('outlined').classes('w-1/2')
                self.edad = ui.number('Edad', value=self.paciente.edad, format='%.0f').props('outlined').classes('w-1/2')
            
            with ui.row().classes('w-full'):
                self.genero = ui.select(['Masculino', 'Femenino', 'Otro'], 
                                      value=self.paciente.genero, label='Género').props('outlined').classes('w-1/2')
                self.telefono = ui.input('Teléfono', value=self.paciente.telefono).props('outlined').classes('w-1/2')
            
            self.email = ui.input('Email', value=self.paciente.email).props('outlined').classes('w-full')
            self.direccion = ui.input('Dirección', value=self.paciente.direccion).props('outlined').classes('w-full')
            
            with ui.expansion('Historial Médico', icon='medical_services').classes('w-full'):
                self.alergias = ui.textarea('Alergias', value=self.paciente.alergias).props('outlined').classes('w-full')
                self.enfermedades = ui.textarea('Enfermedades Crónicas', value=self.paciente.enfermedades_cronicas).props('outlined').classes('w-full')
                self.medicamentos = ui.textarea('Medicamentos', value=self.paciente.medicamentos).props('outlined').classes('w-full')
                self.observaciones = ui.textarea('Observaciones', value=self.paciente.observaciones).props('outlined').classes('w-full')
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Guardar', on_click=self.save, icon='save').props('flat color=primary')
    
    def save(self):
        paciente = Paciente(
            id=self.paciente.id,
            curp=self.curp.value,
            nombre=self.nombre.value,
            apellidos=self.apellidos.value,
            fecha_nacimiento=self.fecha_nacimiento.value,
            edad=int(self.edad.value) if self.edad.value else None,
            genero=self.genero.value,
            telefono=self.telefono.value,
            email=self.email.value,
            direccion=self.direccion.value,
            alergias=self.alergias.value,
            enfermedades_cronicas=self.enfermedades.value,
            medicamentos=self.medicamentos.value,
            observaciones=self.observaciones.value
        )
        
        if self.on_save:
            self.on_save(paciente)