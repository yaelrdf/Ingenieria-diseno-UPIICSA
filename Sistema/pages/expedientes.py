from nicegui import ui
import database as db
from models.paciente import Paciente
from models.procedimiento import ProcedimientoPaciente
from components.paciente_selector import PacienteSelector

class ExpedientesPage:
    def __init__(self, paciente_id=None):
        self.paciente_id = paciente_id
        self.paciente_nombre = ""
        self.create_content()
        # If a paciente_id was provided (via query param), pre-select and load
        if self.paciente_id:
            try:
                self.paciente_id = int(self.paciente_id)
                self.cargar_nombre_paciente()
            except Exception:
                pass
            self.cargar_expediente()
    
    def cargar_nombre_paciente(self):
        sql = "SELECT nombre || ' ' || apellidos FROM pacientes WHERE id = %s"
        res = db.fetch_one(sql, (self.paciente_id,))
        if res:
            self.paciente_nombre = res[0]
            self.label_paciente.set_text(self.paciente_nombre)
            self.paciente_display.set_visibility(True)

    def create_content(self):
        ui.label('Expedientes Clínicos').classes('text-h4 mb-4')
        
        # Selector de paciente
        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector).props('outline color=primary')
            
            self.paciente_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
            with self.paciente_display:
                ui.icon('person', color='primary')
                self.label_paciente = ui.label('Seleccione un paciente').classes('font-bold')
            
            self.paciente_display.set_visibility(self.paciente_id is not None)
        
        # Pestañas para diferentes secciones del expediente
        with ui.tabs(value='info').classes('w-full') as self.tabs:
            ui.tab('info', 'Información General')
            ui.tab('procedimientos', 'Procedimientos Realizados')
            ui.tab('observaciones', 'Notas y Observaciones')

        self.tab_panels = ui.tab_panels(self.tabs, value='info').classes('w-full')

        with self.tab_panels:
            with ui.tab_panel('info'):
                self.info_general = ui.column().classes('w-full')

            with ui.tab_panel('procedimientos'):
                self.procedimientos = ui.column().classes('w-full')

            with ui.tab_panel('observaciones'):
                self.observaciones = ui.column().classes('w-full')
        
        # Inicialmente vacío
        self.mostrar_vacio()
    
    def abrir_selector(self):
        PacienteSelector(on_select=self.seleccionar_paciente).open()
        
    def seleccionar_paciente(self, pid, name):
        self.paciente_id = pid
        self.paciente_nombre = name
        self.label_paciente.set_text(name)
        self.paciente_display.set_visibility(True)
        self.cargar_expediente()

    def mostrar_vacio(self):
        self.info_general.clear()
        self.procedimientos.clear()
        self.observaciones.clear()
        
        with self.info_general:
            ui.label('Seleccione un paciente para ver su expediente').classes('text-italic')
    
    def cargar_expediente(self):
        if not self.paciente_id:
            self.mostrar_vacio()
            return
        
        # Cargar información del expediente
        self.cargar_info_general()
        self.cargar_procedimientos()
        self.cargar_observaciones()
    
    def cargar_info_general(self):
        query = """
        SELECT curp, nombre, apellidos, fecha_nacimiento, edad, genero,
               telefono, email, direccion, alergias, enfermedades_cronicas,
               medicamentos, observaciones, created_at
        FROM pacientes WHERE id = %s
        """
        
        paciente_data = db.fetch_one(query, (self.paciente_id,))
        
        if not paciente_data:
            return
        
        self.info_general.clear()
        
        with self.info_general:
            with ui.card().classes('w-full'):
                ui.label('Datos Personales').classes('text-h6 mb-2')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    # Columna izquierda
                    ui.label(f"Nombre: {paciente_data[1]} {paciente_data[2]}")
                    ui.label(f"CURP: {paciente_data[0]}")
                    ui.label(f"Fecha de Nacimiento: {paciente_data[3]}")
                    ui.label(f"Edad: {paciente_data[4]} años")
                    ui.label(f"Género: {paciente_data[5]}")
                    
                    # Columna derecha
                    ui.label(f"Teléfono: {paciente_data[6]}")
                    ui.label(f"Email: {paciente_data[7]}")
                    ui.label(f"Dirección: {paciente_data[8]}")
                    ui.label(f"Fecha de Registro: {paciente_data[13].strftime('%d/%m/%Y')}")
            
            # Información médica
            with ui.card().classes('w-full mt-4'):
                ui.label('Información Médica').classes('text-h6 mb-2')
                
                if paciente_data[9]:  # Alergias
                    with ui.expansion('Alergias', icon='warning').classes('w-full'):
                        ui.markdown(paciente_data[9]).classes('text-body2')
                
                if paciente_data[10]:  # Enfermedades crónicas
                    with ui.expansion('Enfermedades Crónicas', icon='medical_services').classes('w-full'):
                        ui.markdown(paciente_data[10]).classes('text-body2')
                
                if paciente_data[11]:  # Medicamentos
                    with ui.expansion('Medicamentos Actuales', icon='medication').classes('w-full'):
                        ui.markdown(paciente_data[11]).classes('text-body2')
    
    def cargar_procedimientos(self):
        query = """
        SELECT pp.id, pr.nombre, pp.estado, pp.fecha_realizacion, 
               pp.costo, pp.notas, pp.diente_numero
        FROM procedimientos_paciente pp
        LEFT JOIN procedimientos pr ON pp.procedimiento_id = pr.id
        WHERE pp.paciente_id = %s
        ORDER BY pp.fecha_realizacion DESC NULLS LAST, pp.created_at DESC
        """
        
        procedimientos = db.fetch_all(query, (self.paciente_id,))
        
        self.procedimientos.clear()
        
        with self.procedimientos:
            ui.label('Procedimientos Realizados').classes('text-h6 mb-2')
            
            if not procedimientos:
                ui.label('No hay procedimientos registrados').classes('text-italic')
                return
            
            for proc in procedimientos:
                estado_color = {
                    'pendiente': 'orange',
                    'en_proceso': 'blue',
                    'completado': 'green'
                }.get(proc[2], 'grey')
                
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(proc[1]).classes('font-bold text-lg')
                        ui.badge(proc[2].replace('_', ' ').title(), color=estado_color).props('rounded')
                    
                    with ui.row().classes('w-full gap-4'):
                        if proc[3]:
                            ui.label(f"Fecha: {proc[3]}")
                        if proc[6]:
                            ui.label(f"Diente: {proc[6]}")
                        ui.label(f"Costo: ${proc[4]:,.2f}")
                    
                    if proc[5]:
                        ui.label(proc[5]).classes('text-body2')
    
    def cargar_observaciones(self, edit_mode=False):
        # Cargar observaciones generales del paciente
        query = "SELECT observaciones FROM pacientes WHERE id = %s"
        result = db.fetch_one(query, (self.paciente_id,))
        obs_text = result[0] if result and result[0] else ""
        
        self.observaciones.clear()
        
        with self.observaciones:
            ui.label('Notas y Observaciones').classes('text-h6 mb-2')
            
            if edit_mode:
                self.obs_input = ui.textarea('Observaciones', value=obs_text).props('outlined').classes('w-full')
                with ui.row().classes('mt-4 gap-2'):
                    ui.button('Guardar', on_click=self.guardar_observacion, icon='save').props('flat color=primary')
                    ui.button('Cancelar', on_click=lambda: self.cargar_observaciones(False), icon='cancel').props('flat color=grey')
            else:
                if not obs_text:
                    ui.label('No hay observaciones registradas').classes('text-italic')
                else:
                    ui.label(obs_text).classes('text-body2 whitespace-pre-wrap w-full')
                
                # Botón para editar
                with ui.row().classes('mt-4'):
                    ui.button('Editar', on_click=lambda: self.cargar_observaciones(True), icon='edit').props('flat color=primary')
    
    def guardar_observacion(self):
        nueva_obs = self.obs_input.value
        
        query = "UPDATE pacientes SET observaciones = %s WHERE id = %s"
        
        try:
            db.execute_query(query, (nueva_obs, self.paciente_id))
            ui.notify('Observaciones actualizadas', type='positive')
            self.cargar_observaciones(False)
        except Exception as e:
            ui.notify(f'Error: {str(e)}', type='negative')