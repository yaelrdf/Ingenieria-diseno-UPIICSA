from nicegui import ui
import database as db
from models.paciente import Paciente
from models.procedimiento import ProcedimientoPaciente

class ExpedientesPage:
    def __init__(self, paciente_id=None):
        self.paciente_id = paciente_id
        self.paciente_nombre = ""
        self.create_content()
        # If a paciente_id was provided (via query param), pre-select and load
        if self.paciente_id:
            try:
                self.select_paciente.value = int(self.paciente_id)
            except Exception:
                self.select_paciente.value = self.paciente_id
            self.cargar_expediente()
    
    def create_content(self):
        ui.label('Expedientes Clínicos').classes('text-h4 mb-4')
        
        # Selector de paciente
        with ui.row().classes('w-full items-center mb-4'):
            self.select_paciente = ui.select(
                label='Seleccionar paciente',
                options={},
                on_change=self.cargar_expediente
            ).props('outlined').classes('w-96')
            self.cargar_pacientes_select()
        
        # Pestañas para diferentes secciones del expediente
        # use simple internal names for tabs (no spaces) and labels for display
        self.tabs = ui.tabs(value='info').classes('w-full')
        ui.tab('info', 'Información General')
        ui.tab('historial', 'Historial Médico')
        ui.tab('procedimientos', 'Procedimientos Realizados')
        ui.tab('observaciones', 'Notas y Observaciones')

        self.tab_panels = ui.tab_panels(self.tabs, value='info').classes('w-full')

        with self.tab_panels:
            with ui.tab_panel('info'):
                self.info_general = ui.column().classes('w-full')

            with ui.tab_panel('historial'):
                self.historial_medico = ui.column().classes('w-full')

            with ui.tab_panel('procedimientos'):
                self.procedimientos = ui.column().classes('w-full')

            with ui.tab_panel('observaciones'):
                self.observaciones = ui.column().classes('w-full')
        
        # Inicialmente vacío
        self.mostrar_vacio()
    
    def cargar_pacientes_select(self):
        query = "SELECT id, nombre || ' ' || apellidos as nombre FROM pacientes ORDER BY nombre"
        pacientes = db.fetch_all(query)
        options = {None: 'Seleccione un paciente'}
        for p in pacientes:
            options[p[0]] = p[1]
        self.select_paciente.options = options
    
    def mostrar_vacio(self):
        self.info_general.clear()
        self.historial_medico.clear()
        self.procedimientos.clear()
        self.observaciones.clear()
        
        with self.info_general:
            ui.label('Seleccione un paciente para ver su expediente').classes('text-italic')
    
    def cargar_expediente(self):
        self.paciente_id = self.select_paciente.value
        
        if not self.paciente_id:
            self.mostrar_vacio()
            return
        
        # Cargar información del paciente
        self.cargar_info_general()
        self.cargar_historial_medico()
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
    
    def cargar_historial_medico(self):
        query = """
        SELECT fecha, tipo, descripcion, observaciones, 
               COALESCE(u.nombre, 'Sistema') as realizado_por
        FROM historial_medico hm
        LEFT JOIN usuarios u ON hm.realizado_por = u.id
        WHERE paciente_id = %s
        ORDER BY fecha DESC, created_at DESC
        """
        
        historial = db.fetch_all(query, (self.paciente_id,))
        
        self.historial_medico.clear()
        
        with self.historial_medico:
            ui.label('Historial Médico').classes('text-h6 mb-2')
            
            if not historial:
                ui.label('No hay registro de historial médico').classes('text-italic')
                return
            
            for item in historial:
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(f"{item[0]} - {item[1].title()}").classes('font-bold')
                        ui.label(f"Por: {item[4]}")
                    
                    if item[2]:  # Descripción
                        ui.label(item[2]).classes('text-body2')
                    
                    if item[3]:  # Observaciones
                        with ui.expansion('Observaciones').classes('w-full'):
                            ui.markdown(item[3]).classes('text-body2')
    
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
    
    def cargar_observaciones(self):
        # Cargar observaciones generales del paciente
        query = "SELECT observaciones FROM pacientes WHERE id = %s"
        result = db.fetch_one(query, (self.paciente_id,))
        
        self.observaciones.clear()
        
        with self.observaciones:
            ui.label('Notas y Observaciones').classes('text-h6 mb-2')
            
            if not result or not result[0]:
                ui.label('No hay observaciones registradas').classes('text-italic')
                return
            
            ui.markdown(result[0]).classes('text-body2')
            
            # Botón para agregar nueva observación
            with ui.row().classes('mt-4'):
                self.nueva_obs_input = ui.textarea('Nueva observación').props('outlined').classes('w-full')
                ui.button('Agregar', on_click=self.agregar_observacion, icon='add').props('flat color=primary')
    
    def agregar_observacion(self):
        nueva_obs = self.nueva_obs_input.value
        if not nueva_obs:
            ui.notify('Ingrese una observación', type='warning')
            return
        
        query = """
        UPDATE pacientes 
        SET observaciones = COALESCE(observaciones, '') || '\n\n' || %s || ' - ' || CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            db.execute_query(query, (nueva_obs, self.paciente_id))
            ui.notify('Observación agregada', type='positive')
            self.nueva_obs_input.value = ""
            self.cargar_observaciones()
        except Exception as e:
            ui.notify(f'Error: {str(e)}', type='negative')