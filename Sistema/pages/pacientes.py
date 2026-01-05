from nicegui import ui, app
from components.paciente_form import PacienteForm
import database as db

class PacientesPage:
    def __init__(self):
        user = app.storage.user.get('user', {})
        self.puede_eliminar = user.get('es_superadmin', False) or \
                             (user.get('permisos', {}) if isinstance(user.get('permisos'), dict) else {}).get('puede_eliminar', False)
        self.search_query = ""
        self.pacientes = []
        self.pacientes_container = None
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Pacientes').classes('text-h4 mb-4')
        
        with ui.row().classes('w-full items-center mb-4'):
            self.search_input = ui.input('Buscar paciente', 
                                        on_change=self.buscar_pacientes,
                                        placeholder='Nombre, CURP o teléfono').props('outlined').classes('w-96')
            ui.button('Nuevo Paciente', on_click=self.mostrar_form_nuevo, 
                     icon='person_add').props('flat color=primary')
        
        # Container para las tarjetas
        self.pacientes_container = ui.column().classes('w-full gap-3')
        
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
        
        # Limpiar el contenedor
        self.pacientes_container.clear()
        
        if not resultados:
            with self.pacientes_container:
                ui.label('No hay pacientes registrados').classes('text-subtitle2 italic text-gray-500')
            return
        
        # Crear tarjetas para cada paciente
        with self.pacientes_container:
            for paciente in resultados:
                self.crear_tarjeta_paciente(paciente[0], paciente[1], paciente[2], paciente[3], paciente[4])
    
    def crear_tarjeta_paciente(self, paciente_id, nombre, curp, telefono, email):
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-start'):
                # Información del paciente
                with ui.column().classes('flex-grow'):
                    ui.label(nombre).classes('text-h6 font-bold')
                    
                    with ui.row().classes('gap-8'):
                        with ui.column().classes('gap-1'):
                            ui.label('CURP').classes('text-caption text-gray-600')
                            ui.label(curp).classes('text-body2 font-mono')
                        
                        with ui.column().classes('gap-1'):
                            ui.label('Teléfono').classes('text-caption text-gray-600')
                            ui.label(telefono).classes('text-body2')
                        
                        with ui.column().classes('gap-1'):
                            ui.label('Email').classes('text-caption text-gray-600')
                            ui.label(email).classes('text-body2 break-all')
                
                # Botones de acción
                with ui.column().classes('items-end gap-2'):
                    with ui.row().classes('gap-2'):
                        ui.button(icon='edit', on_click=lambda id=paciente_id: self.editar_paciente(id)).props('flat')
                        ui.button(icon='visibility', on_click=lambda id=paciente_id: self.ver_expediente(id)).props('flat color=blue')
                    if self.puede_eliminar:
                        ui.button(icon='delete', on_click=lambda id=paciente_id: self.eliminar_paciente(id)).props('flat color=red')
    
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
        sql = "SELECT id, curp, nombre, apellidos, fecha_nacimiento, edad, genero, telefono, email, direccion, alergias, enfermedades_cronicas, medicamentos, observaciones FROM pacientes WHERE id = %s"
        paciente_data = db.fetch_one(sql, (paciente_id,))
        
        if not paciente_data:
            ui.notify('Paciente no encontrado', type='warning')
            return
        
        from models.paciente import Paciente
        paciente = Paciente(
            id=paciente_data[0],
            curp=paciente_data[1],
            nombre=paciente_data[2],
            apellidos=paciente_data[3],
            fecha_nacimiento=paciente_data[4],
            edad=paciente_data[5],
            genero=paciente_data[6],
            telefono=paciente_data[7],
            email=paciente_data[8],
            direccion=paciente_data[9],
            alergias=paciente_data[10],
            enfermedades_cronicas=paciente_data[11],
            medicamentos=paciente_data[12],
            observaciones=paciente_data[13]
        )

        def actualizar_paciente(p):
            sql = """
            UPDATE pacientes SET 
                curp=%s, nombre=%s, apellidos=%s, fecha_nacimiento=%s, 
                edad=%s, genero=%s, telefono=%s, email=%s, direccion=%s, 
                alergias=%s, enfermedades_cronicas=%s, medicamentos=%s, observaciones=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
            """
            params = (
                p.curp, p.nombre, p.apellidos, p.fecha_nacimiento,
                p.edad, p.genero, p.telefono, p.email, p.direccion,
                p.alergias, p.enfermedades_cronicas, p.medicamentos, p.observaciones,
                p.id
            )
            try:
                db.execute_query(sql, params)
                ui.notify('Paciente actualizado exitosamente', type='positive')
                self.cargar_pacientes()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {str(e)}', type='negative')

        dialog = ui.dialog()
        with dialog:
            PacienteForm(paciente=paciente, on_save=actualizar_paciente, on_cancel=dialog.close)
        dialog.open()
    
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