from nicegui import ui

from nicegui import ui, app
import database as db
from models.usuario_sistema import UsuarioSistema
from components.usuario_sistema_form import UsuarioSistemaForm
import json

class UsuariosPage:
    def __init__(self):
        self.usuarios_container = None
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Usuarios del Sistema').classes('text-h4 mb-4')
        
        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Nuevo Usuario', on_click=self.mostrar_form_nuevo, 
                     icon='person_add').props('flat color=primary')
            
            self.search_input = ui.input(placeholder='Buscar por nombre o usuario...', 
                                       on_change=self.cargar_usuarios).props('outlined dense clearable').classes('flex-grow')
            with self.search_input:
                ui.icon('search')
        
        # Container para las tarjetas
        self.usuarios_container = ui.column().classes('w-full gap-3')
        
        self.cargar_usuarios()
    
    def cargar_usuarios(self):
        search_term = self.search_input.value if hasattr(self, 'search_input') and self.search_input.value else ""
        
        sql = "SELECT id, username, nombre, puesto, es_superadmin, permisos, medico_id, password FROM usuarios_sistema"
        params = []
        
        if search_term:
            sql += " WHERE nombre ILIKE %s OR username ILIKE %s"
            term = f"%{search_term}%"
            params = [term, term]
            
        sql += " ORDER BY nombre"
        resultados = db.fetch_all(sql, params)
        
        self.usuarios_container.clear()
        
        if not resultados:
            with self.usuarios_container:
                ui.label('No hay usuarios registrados').classes('text-subtitle2 italic text-gray-500')
            return
        
        with self.usuarios_container:
            for u_data in resultados:
                self.crear_tarjeta_usuario(u_data)
    
    def crear_tarjeta_usuario(self, data):
        u_id, username, nombre, puesto, es_superadmin, permisos, medico_id, password = data
        
        if isinstance(permisos, str):
            permisos = json.loads(permisos)

        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-start'):
                with ui.column().classes('flex-grow'):
                    with ui.row().classes('items-center gap-2'):
                        ui.label(nombre).classes('text-h6 font-bold')
                        ui.label(f"(@{username})").classes('text-subtitle2 text-grey-6')
                        if es_superadmin:
                            ui.badge('Super Admin', color='amber').props('rounded')
                    
                    with ui.row().classes('gap-8'):
                        with ui.column().classes('gap-1'):
                            ui.label('Puesto').classes('text-caption text-gray-600')
                            ui.label(puesto or 'N/A').classes('text-body2')
                        
                        with ui.column().classes('gap-1'):
                            ui.label('Permisos').classes('text-caption text-gray-600')
                            p_text = f"{len(permisos.get('menus', []))} menús"
                            if permisos.get('puede_eliminar'):
                                p_text += ", puede eliminar"
                            ui.label(p_text).classes('text-body2')

                with ui.column().classes('items-end gap-2'):
                    with ui.row().classes('gap-2'):
                        ui.button(icon='edit', on_click=lambda: self.editar_usuario(data)).props('flat')
                        if username != 'admin':
                            ui.button(icon='delete', on_click=lambda u=u_id, name=username: self.eliminar_usuario(u, name)).props('flat color=red')

    def mostrar_form_nuevo(self):
        def guardar(usuario):
            sql = """
            INSERT INTO usuarios_sistema (username, password, nombre, puesto, es_superadmin, permisos, medico_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (usuario.username, usuario.password, usuario.nombre, usuario.puesto, 
                      usuario.es_superadmin, json.dumps(usuario.permisos), usuario.medico_id)
            
            try:
                db.execute_query(sql, params)
                ui.notify('Usuario creado exitosamente', type='positive')
                self.cargar_usuarios()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar: {str(e)}', type='negative')
        
        dialog = ui.dialog().classes('w-full max-w-md')
        with dialog:
            UsuarioSistemaForm(on_save=guardar, on_cancel=dialog.close)
        dialog.open()

    def editar_usuario(self, data):
        u_id, username, nombre, puesto, es_superadmin, permisos, medico_id, password = data
        if isinstance(permisos, str):
            permisos = json.loads(permisos)
            
        usuario = UsuarioSistema(
            id=u_id, username=username, nombre=nombre, puesto=puesto, 
            es_superadmin=es_superadmin, permisos=permisos, medico_id=medico_id,
            password=password
        )

        def actualizar(u):
            sql = """
            UPDATE usuarios_sistema SET username=%s, password=%s, nombre=%s, puesto=%s, 
                                      es_superadmin=%s, permisos=%s, medico_id=%s
            WHERE id=%s
            """
            params = (u.username, u.password, u.nombre, u.puesto, 
                      u.es_superadmin, json.dumps(u.permisos), u.medico_id, u.id)
            try:
                db.execute_query(sql, params)
                ui.notify('Usuario actualizado', type='positive')
                self.cargar_usuarios()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {str(e)}', type='negative')

        dialog = ui.dialog().classes('w-full max-w-md')
        with dialog:
            UsuarioSistemaForm(usuario=usuario, on_save=actualizar, on_cancel=dialog.close)
        dialog.open()

    def eliminar_usuario(self, u_id, username):
        if username == 'admin':
            ui.notify('No se puede eliminar el usuario administrador por defecto', type='warning')
            return

        current_user_id = app.storage.user.get('user', {}).get('id')
        if u_id == current_user_id:
             ui.notify('No puedes eliminar tu propia cuenta', type='warning')
             return

        def confirmar():
            try:
                db.execute_query("DELETE FROM usuarios_sistema WHERE id = %s", (u_id,))
                ui.notify('Usuario eliminado', type='positive')
                self.cargar_usuarios()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Eliminar usuario?').classes('text-h6')
                with ui.row().classes('justify-end'):
                    ui.button('Cancelar', on_click=dialog.close)
                    ui.button('Eliminar', on_click=confirmar, color='red')
        dialog.open()
