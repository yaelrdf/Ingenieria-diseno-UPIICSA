from nicegui import ui
from datetime import datetime, date, timedelta
import database as db
from models.cita import Cita
from components.cita_form import CitaForm

class CitasPage:
    def __init__(self):
        self.fecha_seleccionada = date.today()
        self.paciente_id = None
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Citas').classes('text-h4 mb-4')
        
        # Filtros
        with ui.row().classes('w-full items-center mb-4'):
            self.fecha_input = ui.date(value=self.fecha_seleccionada, 
                                      on_change=self.cargar_citas).props('outlined')
            ui.button('Hoy', on_click=lambda: self.set_fecha_hoy()).props('flat')
            ui.button('+ Nueva Cita', on_click=self.mostrar_form_nueva_cita, 
                     icon='add').props('flat color=primary')
        
        # Selector de paciente para filtrar
        with ui.row().classes('w-full mb-4'):
            self.select_paciente = ui.select(
                label='Filtrar por paciente',
                options={},
                on_change=lambda: self.cargar_citas()
            ).props('outlined clearable').classes('w-64')
            self.cargar_pacientes_select()
        
        # Tabla de citas
        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
            {'name': 'hora', 'label': 'Hora', 'field': 'hora', 'sortable': True},
            {'name': 'paciente', 'label': 'Paciente', 'field': 'paciente', 'sortable': True},
            {'name': 'tipo', 'label': 'Tipo', 'field': 'tipo', 'sortable': True},
            {'name': 'procedimiento', 'label': 'Procedimiento', 'field': 'procedimiento'},
            {'name': 'doctor', 'label': 'Doctor', 'field': 'doctor'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'},
            {'name': 'acciones', 'label': 'Acciones', 'field': 'acciones'}
        ]
        
        self.citas_table = ui.table(
            columns=columns,
            rows=[],
            row_key='id',
            pagination=10
        ).classes('w-full')
        
        self.cargar_citas()
    
    def set_fecha_hoy(self):
        self.fecha_input.value = date.today()
        self.cargar_citas()
    
    def cargar_pacientes_select(self):
        query = "SELECT id, nombre || ' ' || apellidos as nombre FROM pacientes ORDER BY nombre"
        pacientes = db.fetch_all(query)
        options = {None: 'Todos los pacientes'}
        for p in pacientes:
            options[p[0]] = p[1]
        self.select_paciente.options = options
    
    def cargar_citas(self):
        fecha = self.fecha_input.value
        paciente_id = self.select_paciente.value
        
        query = """
        SELECT c.id, 
               TO_CHAR(c.fecha_hora, 'HH24:MI') as hora,
               p.nombre || ' ' || p.apellidos as paciente,
               c.tipo,
               c.procedimiento,
               COALESCE(u.nombre, 'Sin asignar') as doctor,
               c.estado
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        LEFT JOIN usuarios u ON c.doctor_id = u.id
        WHERE DATE(c.fecha_hora) = %s
        """
        
        params = [fecha]
        
        if paciente_id:
            query += " AND c.paciente_id = %s"
            params.append(paciente_id)
        
        query += " ORDER BY c.fecha_hora"
        
        citas = db.fetch_all(query, params)
        
        rows = []
        for cita in citas:
            estado_color = {
                'programada': 'blue',
                'en_curso': 'orange',
                'completada': 'green',
                'cancelada': 'red'
            }.get(cita[6], 'grey')
            
            rows.append({
                'id': cita[0],
                'hora': cita[1],
                'paciente': cita[2],
                'tipo': cita[3],
                'procedimiento': cita[4],
                'doctor': cita[5],
                'estado': self.get_estado_badge(cita[6], estado_color),
                'acciones': self.crear_botones_accion(cita[0], cita[6])
            })
        
        self.citas_table.rows = rows
    
    def get_estado_badge(self, estado, color):
        with ui.element('div'):
            ui.badge(estado.replace('_', ' ').title(), color=color).props('rounded')
        return ''
    
    def crear_botones_accion(self, cita_id, estado):
        with ui.row().classes('gap-1'):
            if estado in ['programada', 'en_curso']:
                ui.button(icon='edit', on_click=lambda id=cita_id: self.editar_cita(id)).props('flat dense')
                ui.button(icon='cancel', on_click=lambda id=cita_id: self.cancelar_cita(id)).props('flat dense color=orange')
            
            if estado == 'programada':
                ui.button(icon='play_arrow', on_click=lambda id=cita_id: self.iniciar_cita(id)).props('flat dense color=green')
            
            if estado == 'en_curso':
                ui.button(icon='check', on_click=lambda id=cita_id: self.completar_cita(id)).props('flat dense color=green')
            
            ui.button(icon='delete', on_click=lambda id=cita_id: self.eliminar_cita(id)).props('flat dense color=red')
        return ''
    
    def mostrar_form_nueva_cita(self):
        def guardar_cita(cita):
            query = """
            INSERT INTO citas (paciente_id, doctor_id, fecha_hora, tipo, 
                             procedimiento, estado, notas, duracion_minutos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                cita.paciente_id, cita.doctor_id, cita.fecha_hora, cita.tipo,
                cita.procedimiento, cita.estado, cita.notas, cita.duracion_minutos
            )
            
            try:
                db.execute_query(query, params)
                ui.notify('Cita guardada exitosamente', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar cita: {str(e)}', type='negative')
        
        dialog = ui.dialog().classes('w-full max-w-2xl')
        with dialog:
            CitaForm(on_save=guardar_cita, on_cancel=dialog.close)
        dialog.open()
    
    def editar_cita(self, cita_id):
        query = """
        SELECT id, paciente_id, doctor_id, fecha_hora, tipo, 
               procedimiento, estado, notas, duracion_minutos
        FROM citas WHERE id = %s
        """
        cita_data = db.fetch_one(query, (cita_id,))
        
        if not cita_data:
            ui.notify('Cita no encontrada', type='warning')
            return
        
        cita = Cita(
            id=cita_data[0],
            paciente_id=cita_data[1],
            doctor_id=cita_data[2],
            fecha_hora=cita_data[3],
            tipo=cita_data[4],
            procedimiento=cita_data[5],
            estado=cita_data[6],
            notas=cita_data[7],
            duracion_minutos=cita_data[8]
        )
        
        def actualizar_cita(cita_actualizada):
            query = """
            UPDATE citas SET paciente_id = %s, doctor_id = %s, fecha_hora = %s,
                          tipo = %s, procedimiento = %s, estado = %s,
                          notas = %s, duracion_minutos = %s
            WHERE id = %s
            """
            
            params = (
                cita_actualizada.paciente_id, cita_actualizada.doctor_id,
                cita_actualizada.fecha_hora, cita_actualizada.tipo,
                cita_actualizada.procedimiento, cita_actualizada.estado,
                cita_actualizada.notas, cita_actualizada.duracion_minutos,
                cita_id
            )
            
            try:
                db.execute_query(query, params)
                ui.notify('Cita actualizada', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {str(e)}', type='negative')
        
        dialog = ui.dialog().classes('w-full max-w-2xl')
        with dialog:
            CitaForm(cita=cita, on_save=actualizar_cita, on_cancel=dialog.close)
        dialog.open()
    
    def iniciar_cita(self, cita_id):
        def confirmar_inicio():
            try:
                db.execute_query("UPDATE citas SET estado = 'en_curso' WHERE id = %s", (cita_id,))
                ui.notify('Cita iniciada', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Iniciar cita?').classes('text-h6')
                ui.label('La cita cambiará a estado "en curso".')
                with ui.row().classes('justify-end'):
                    ui.button('Cancelar', on_click=dialog.close)
                    ui.button('Iniciar', on_click=confirmar_inicio, color='green')
        dialog.open()
    
    def completar_cita(self, cita_id):
        def confirmar_completar():
            try:
                db.execute_query("UPDATE citas SET estado = 'completada' WHERE id = %s", (cita_id,))
                ui.notify('Cita completada', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Completar cita?').classes('text-h6')
                ui.label('La cita cambiará a estado "completada".')
                with ui.row().classes('justify-end'):
                    ui.button('Cancelar', on_click=dialog.close)
                    ui.button('Completar', on_click=confirmar_completar, color='green')
        dialog.open()
    
    def cancelar_cita(self, cita_id):
        def confirmar_cancelar():
            try:
                db.execute_query("UPDATE citas SET estado = 'cancelada' WHERE id = %s", (cita_id,))
                ui.notify('Cita cancelada', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Cancelar cita?').classes('text-h6')
                ui.label('La cita cambiará a estado "cancelada".')
                with ui.row().classes('justify-end'):
                    ui.button('No', on_click=dialog.close)
                    ui.button('Sí, cancelar', on_click=confirmar_cancelar, color='orange')
        dialog.open()
    
    def eliminar_cita(self, cita_id):
        def confirmar_eliminar():
            try:
                db.execute_query("DELETE FROM citas WHERE id = %s", (cita_id,))
                ui.notify('Cita eliminada', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al eliminar: {str(e)}', type='negative')
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('¿Eliminar cita permanentemente?').classes('text-h6')
                ui.label('Esta acción no se puede deshacer.')
                with ui.row().classes('justify-end'):
                    ui.button('Cancelar', on_click=dialog.close)
                    ui.button('Eliminar', on_click=confirmar_eliminar, color='red')
        dialog.open()