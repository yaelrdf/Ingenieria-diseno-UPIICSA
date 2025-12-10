from nicegui import ui
from components.paciente_form import PacienteForm
import database as db

class PacientesPage:
    def __init__(self):
        self.search_query = ""
        self.pacientes = []
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Pacientes').classes('text-h4 mb-4')
        
        with ui.row().classes('w-full items-center mb-4'):
            self.search_input = ui.input('Buscar paciente', 
                                        on_change=self.buscar_pacientes,
                                        placeholder='Nombre, CURP o teléfono').props('outlined').classes('w-96')
            ui.button('Nuevo Paciente', on_click=self.mostrar_form_nuevo, 
                     icon='person_add').props('flat color=primary')
        
        self.pacientes_table = ui.table(
            columns=[
                {'name': 'id', 'label': 'ID', 'field': 'id'},
                {'name': 'nombre', 'label': 'Nombre', 'field': 'nombre'},
                {'name': 'curp', 'label': 'CURP', 'field': 'curp'},
                {'name': 'telefono', 'label': 'Teléfono', 'field': 'telefono'},
                {'name': 'email', 'label': 'Email', 'field': 'email'},
                {'name': 'acciones', 'label': 'Acciones', 'field': 'acciones'}
            ],
            rows=[],
            row_key='id'
        ).classes('w-full')
        
        self.cargar_pacientes()
    
    def cargar_pacientes(self, query=None):
        if query:
            search = f"%{query}%"
            sql = """
            SELECT id, nombre || ' ' || apellidos as nombre, curp, telefono, email
            FROM pacientes 
            WHERE nombre ILIKE %s OR apellidos ILIKE %s OR curp ILIKE %s OR telefono ILIKE %s
            ORDER BY nombre
            """
            resultados = db.fetch_all(sql, (search, search, search, search))
        else:
            sql = "SELECT id, nombre || ' ' || apellidos as nombre, curp, telefono, email FROM pacientes ORDER BY nombre"
            resultados = db.fetch_all(sql)
        
        rows = []
        for paciente in resultados:
            rows.append({
                'id': paciente[0],
                'nombre': paciente[1],
                'curp': paciente[2],
                'telefono': paciente[3],
                'email': paciente[4],
                'acciones': self.crear_botones_accion(paciente[0])
            })
        
        self.pacientes_table.rows = rows
    
    def crear_botones_accion(self, paciente_id):
        with ui.row().classes('gap-1'):
            ui.button(icon='edit', on_click=lambda id=paciente_id: self.editar_paciente(id)).props('flat dense')
            ui.button(icon='delete', on_click=lambda id=paciente_id: self.eliminar_paciente(id)).props('flat dense color=red')
            ui.button(icon='visibility', on_click=lambda id=paciente_id: self.ver_expediente(id)).props('flat dense color=green')
    
    def buscar_pacientes(self):
        query = self.search_input.value
        self.cargar_pacientes(query)
    
    def mostrar_form_nuevo(self):
        def guardar_paciente(paciente):
            sql = """
            INSERT INTO pacientes (curp, nombre, apellidos, fecha_nacimiento, edad, genero, 
                                  telefono, email, direccion, alergias, enfermedades_cronicas, 
                                  medicamentos, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            params = (
                paciente.curp, paciente.nombre, paciente.apellidos, paciente.fecha_nacimiento,
                paciente.edad, paciente.genero, paciente.telefono, paciente.email,
                paciente.direccion, paciente.alergias, paciente.enfermedades_cronicas,
                paciente.medicamentos, paciente.observaciones
            )
            
            try:
                db.execute_query(sql, params)
                ui.notify('Paciente guardado exitosamente', type='positive')
                self.cargar_pacientes()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            PacienteForm(on_save=guardar_paciente, on_cancel=dialog.close)
        dialog.open()
    
    def editar_paciente(self, paciente_id):
        # Implementar edición similar al formulario nuevo
        pass
    
    def eliminar_paciente(self, paciente_id):
        def confirmar_eliminacion():
            try:
                db.execute_query("DELETE FROM pacientes WHERE id = %s", (paciente_id,))
                ui.notify('Paciente eliminado', type='positive')
                self.cargar_pacientes()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al eliminar: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Eliminar paciente?').classes('text-h6')
                ui.label('Esta acción no se puede deshacer.')
                with ui.row().classes('justify-end'):
                    ui.button('Cancelar', on_click=dialog.close)
                    ui.button('Eliminar', on_click=confirmar_eliminacion, color='red')
        dialog.open()
    
    def ver_expediente(self, paciente_id):
        # Aquí se podría redirigir a la página de expedientes con el paciente seleccionado
        ui.navigate.to(f'/expedientes?paciente_id={paciente_id}')