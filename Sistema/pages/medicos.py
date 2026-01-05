from nicegui import ui, app
import database as db
from models.usuario import Usuario
from components.usuario_form import UsuarioForm
from datetime import datetime

class MedicosPage:
    def __init__(self):
        user = app.storage.user.get('user', {})
        self.puede_eliminar = user.get('es_superadmin', False) or \
                             (user.get('permisos', {}) if isinstance(user.get('permisos'), dict) else {}).get('puede_eliminar', False)
        self.medicos_container = None
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Médicos').classes('text-h4 mb-4')
        
        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Nuevo Médico', on_click=self.mostrar_form_nuevo, 
                     icon='person_add').props('flat color=primary')
            
            self.search_input = ui.input(placeholder='Buscar por nombre, email o teléfono...', 
                                       on_change=self.cargar_medicos).props('outlined dense clearable').classes('flex-grow')
            with self.search_input:
                ui.icon('search')
        
        # Container para las tarjetas
        self.medicos_container = ui.column().classes('w-full gap-3')
        
        self.cargar_medicos()
    
    def cargar_medicos(self):
        search_term = self.search_input.value if hasattr(self, 'search_input') and self.search_input.value else ""
        
        sql = "SELECT id, nombre, email, telefono, especialidad, activo FROM usuarios"
        params = []
        
        if search_term:
            sql += " WHERE nombre ILIKE %s OR email ILIKE %s OR telefono ILIKE %s"
            term = f"%{search_term}%"
            params = [term, term, term]
            
        sql += " ORDER BY nombre"
        resultados = db.fetch_all(sql, params)
        
        self.medicos_container.clear()
        
        if not resultados:
            with self.medicos_container:
                ui.label('No hay médicos registrados').classes('text-subtitle2 italic text-gray-500')
            return
        
        with self.medicos_container:
            for m in resultados:
                self.crear_tarjeta_medico(m)
    
    def crear_tarjeta_medico(self, data):
        medico_id, nombre, email, telefono, especialidad, activo = data
        
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-start'):
                # Información del médico
                with ui.column().classes('flex-grow'):
                    with ui.row().classes('items-center gap-2'):
                        ui.label(nombre).classes('text-h6 font-bold')
                        if not activo:
                            ui.badge('Inactivo', color='red').props('rounded')
                    
                    with ui.row().classes('gap-8'):
                        with ui.column().classes('gap-1'):
                            ui.label('Especialidad').classes('text-caption text-gray-600')
                            ui.label(especialidad or 'N/A').classes('text-body2')
                        
                        with ui.column().classes('gap-1'):
                            ui.label('Teléfono').classes('text-caption text-gray-600')
                            ui.label(telefono or 'N/A').classes('text-body2')
                        
                        with ui.column().classes('gap-1'):
                            ui.label('Email').classes('text-caption text-gray-600')
                            ui.label(email).classes('text-body2 break-all')
                
                # Botones de acción
                with ui.column().classes('items-end gap-2'):
                    with ui.row().classes('gap-2'):
                        ui.button(icon='edit', on_click=lambda id=medico_id: self.editar_medico(id)).props('flat')
                        ui.button(icon='event', on_click=lambda id=medico_id: self.ver_citas(id)).props('flat color=blue').tooltip('Ver Citas')
                        if self.puede_eliminar:
                            ui.button(icon='delete', on_click=lambda id=medico_id: self.eliminar_medico(id)).props('flat color=red')

    def mostrar_form_nuevo(self):
        def guardar_medico(usuario):
            sql = """
            INSERT INTO usuarios (nombre, email, telefono, especialidad, activo)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (usuario.nombre, usuario.email, usuario.telefono, usuario.especialidad, usuario.activo)
            
            try:
                db.execute_query(sql, params)
                ui.notify('Médico guardado exitosamente', type='positive')
                self.cargar_medicos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar: {str(e)}', type='negative')
        
        dialog = ui.dialog().classes('w-full max-w-md')
        with dialog:
            UsuarioForm(on_save=guardar_medico, on_cancel=dialog.close)
        dialog.open()

    def editar_medico(self, medico_id):
        sql = "SELECT id, nombre, email, telefono, especialidad, activo FROM usuarios WHERE id = %s"
        data = db.fetch_one(sql, (medico_id,))
        
        if not data:
            ui.notify('Médico no encontrado', type='warning')
            return
        
        usuario = Usuario(id=data[0], nombre=data[1], email=data[2], telefono=data[3], especialidad=data[4], activo=data[5])

        def actualizar_medico(u):
            sql = """
            UPDATE usuarios SET nombre=%s, email=%s, telefono=%s, especialidad=%s, activo=%s
            WHERE id=%s
            """
            params = (u.nombre, u.email, u.telefono, u.especialidad, u.activo, u.id)
            try:
                db.execute_query(sql, params)
                ui.notify('Médico actualizado exitosamente', type='positive')
                self.cargar_medicos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {str(e)}', type='negative')

        dialog = ui.dialog().classes('w-full max-w-md')
        with dialog:
            UsuarioForm(usuario=usuario, on_save=actualizar_medico, on_cancel=dialog.close)
        dialog.open()

    def eliminar_medico(self, medico_id):
        def confirmar_eliminacion():
            try:
                db.execute_query("DELETE FROM usuarios WHERE id = %s", (medico_id,))
                ui.notify('Médico eliminado', type='positive')
                self.cargar_medicos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al eliminar: {str(e)} (Probablemente tiene citas asociadas)', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Eliminar médico?').classes('text-h6')
                ui.label('Esta acción no se puede deshacer.')
                with ui.row().classes('justify-end'):
                    ui.button('Cancelar', on_click=dialog.close)
                    ui.button('Eliminar', on_click=confirmar_eliminacion, color='red')
        dialog.open()

    def ver_citas(self, medico_id):
        sql = "SELECT nombre FROM usuarios WHERE id = %s"
        nombre = db.fetch_one(sql, (medico_id,))[0]
        
        dialog = ui.dialog().classes('w-full max-w-4xl')
        with dialog, ui.card().classes('w-full'):
            ui.label(f'Citas del {nombre}').classes('text-h6 mb-4')
            
            columns = [
                {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha', 'sortable': True},
                {'name': 'hora', 'label': 'Hora', 'field': 'hora', 'sortable': True},
                {'name': 'paciente', 'label': 'Paciente', 'field': 'paciente', 'sortable': True},
                {'name': 'tipo', 'label': 'Tipo', 'field': 'tipo'},
                {'name': 'estado', 'label': 'Estado', 'field': 'estado'}
            ]
            
            query = """
            SELECT TO_CHAR(c.fecha_hora, 'DD/MM/YYYY') as fecha,
                   TO_CHAR(c.fecha_hora, 'HH24:MI') as hora,
                   p.nombre || ' ' || p.apellidos as paciente,
                   c.tipo,
                   c.estado
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            WHERE c.doctor_id = %s
            ORDER BY c.fecha_hora DESC
            """
            citas = db.fetch_all(query, (medico_id,))
            
            rows = []
            for c in citas:
                rows.append({
                    'fecha': c[0],
                    'hora': c[1],
                    'paciente': c[2],
                    'tipo': c[3].replace('_', ' ').title(),
                    'estado': c[4].replace('_', ' ').title()
                })
            
            ui.table(columns=columns, rows=rows, pagination=10).classes('w-full')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cerrar', on_click=dialog.close).props('flat')
        
        dialog.open()
