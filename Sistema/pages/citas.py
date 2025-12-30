from nicegui import ui
from datetime import datetime, date, timedelta
import database as db
from models.cita import Cita
from components.cita_form import CitaForm
from components.paciente_selector import PacienteSelector

class CitasPage:
    def __init__(self):
        self.fecha_seleccionada = date.today()
        self.paciente_id = None
        self.paciente_nombre_filtro = "Todos los pacientes"
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Citas').classes('text-h4 mb-4')
        
        # Diálogo para seleccionar fecha
        with ui.dialog() as self.dialog_fecha:
            with ui.card():
                self.fecha_input = ui.date(value=self.fecha_seleccionada, 
                                          on_change=self.on_date_change).props('outlined')

        # Barra de Herramientas (Filtros y Acciones)
        with ui.row().classes('w-full items-center mb-4 gap-4'):
            # Selector de fecha
            with ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded cursor-pointer').on('click', self.dialog_fecha.open):
                ui.icon('calendar_today', color='primary')
                self.label_fecha = ui.label(self.fecha_seleccionada.strftime('%d/%m/%Y')).classes('font-bold')
                ui.icon('arrow_drop_down', color='primary')

            ui.button('Hoy', on_click=self.set_fecha_hoy).props('flat')
            
            ui.separator().props('vertical').classes('h-8')

            # Selector de paciente para filtrar
            ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector_filtro).props('outline color=primary')
            
            self.paciente_filtro_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
            with self.paciente_filtro_display:
                ui.icon('person', color='primary')
                self.label_paciente_filtro = ui.label(self.paciente_nombre_filtro).classes('font-bold')
                ui.button(icon='close', on_click=self.limpiar_filtro_paciente).props('flat dense color=grey')
            
            self.paciente_filtro_display.set_visibility(self.paciente_id is not None)

            ui.space()

            ui.button('Nueva Cita', on_click=self.mostrar_form_nueva_cita,
                     icon='add').props('flat color=primary')
        
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
        
        # Slots para renderizado personalizado
        self.citas_table.add_slot('body-cell-estado', '''
            <q-td :props="props">
                <q-badge :color="props.row.estado_color" rounded>
                    {{ props.value.replace('_', ' ') }}
                </q-badge>
            </q-td>
        ''')
        
        self.citas_table.add_slot('body-cell-acciones', '''
            <q-td :props="props">
                <q-btn flat round dense icon="edit" @click="$parent.$emit('edit', props.row.id)" v-if="['programada', 'en_curso'].includes(props.row.estado)"></q-btn>
                <q-btn flat round dense icon="cancel" color="orange" @click="$parent.$emit('cancel', props.row.id)" v-if="['programada', 'en_curso'].includes(props.row.estado)"></q-btn>
                <q-btn flat round dense icon="play_arrow" color="green" @click="$parent.$emit('start', props.row.id)" v-if="props.row.estado === 'programada'"></q-btn>
                <q-btn flat round dense icon="check" color="green" @click="$parent.$emit('complete', props.row.id)" v-if="props.row.estado === 'en_curso'"></q-btn>
                <q-btn flat round dense icon="delete" color="red" @click="$parent.$emit('delete', props.row.id)"></q-btn>
            </q-td>
        ''')
        
        # Manejadores de eventos para los botones de la tabla
        self.citas_table.on('edit', lambda e: self.editar_cita(e.args))
        self.citas_table.on('cancel', lambda e: self.cancelar_cita(e.args))
        self.citas_table.on('start', lambda e: self.iniciar_cita(e.args))
        self.citas_table.on('complete', lambda e: self.completar_cita(e.args))
        self.citas_table.on('delete', lambda e: self.eliminar_cita(e.args))
        
        self.cargar_citas()
    
    def set_fecha_hoy(self):
        self.fecha_input.value = date.today()
        self.actualizar_vista_fecha()
        self.cargar_citas()
    
    def on_date_change(self, e):
        self.dialog_fecha.close()
        self.actualizar_vista_fecha()
        self.cargar_citas()

    def actualizar_vista_fecha(self):
        val = self.fecha_input.value
        if isinstance(val, str):
            d = date.fromisoformat(val)
        else:
            d = val
        self.label_fecha.set_text(d.strftime('%d/%m/%Y'))
    
    def abrir_selector_filtro(self):
        PacienteSelector(on_select=self.aplicar_filtro_paciente).open()
        
    def aplicar_filtro_paciente(self, pid, name):
        self.paciente_id = pid
        self.paciente_nombre_filtro = name
        self.label_paciente_filtro.set_text(name)
        self.paciente_filtro_display.set_visibility(True)
        self.cargar_citas()
        
    def limpiar_filtro_paciente(self):
        self.paciente_id = None
        self.paciente_nombre_filtro = "Todos los pacientes"
        self.label_paciente_filtro.set_text(self.paciente_nombre_filtro)
        self.paciente_filtro_display.set_visibility(False)
        self.cargar_citas()

    def cargar_citas(self):
        fecha = self.fecha_input.value
        paciente_id = self.paciente_id
        
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
                'estado': cita[6],
                'estado_color': estado_color
            })
        
        self.citas_table.rows = rows
    
    # Estos métodos ya no son necesarios pero los mantenemos para no romper referencias si las hubiera
    def get_estado_badge(self, estado, color):
        return ''
    
    def crear_botones_accion(self, cita_id, estado):
        return ''
    
    def mostrar_form_nueva_cita(self):
        def guardar_cita(cita):
            query = """
            INSERT INTO citas (paciente_id, doctor_id, fecha_hora, tipo, 
                             procedimiento, estado, notas, duracion_minutos, costo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                cita.paciente_id, cita.doctor_id, cita.fecha_hora, cita.tipo,
                cita.procedimiento, cita.estado, cita.notas, cita.duracion_minutos,
                cita.costo
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
               procedimiento, estado, notas, duracion_minutos, costo
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
            duracion_minutos=cita_data[8],
            costo=cita_data[9]
        )
        
        def actualizar_cita(cita_actualizada):
            query = """
            UPDATE citas SET paciente_id = %s, doctor_id = %s, fecha_hora = %s,
                          tipo = %s, procedimiento = %s, estado = %s,
                          notas = %s, duracion_minutos = %s, costo = %s
            WHERE id = %s
            """
            
            params = (
                cita_actualizada.paciente_id, cita_actualizada.doctor_id,
                cita_actualizada.fecha_hora, cita_actualizada.tipo,
                cita_actualizada.procedimiento, cita_actualizada.estado,
                cita_actualizada.notas, cita_actualizada.duracion_minutos,
                cita_actualizada.costo,
                cita_id
            )
            
            try:
                db.execute_query(query, params)
                
                # Sincronizar con procedimientos_paciente if completada
                if cita_actualizada.estado == 'completada' and float(cita_actualizada.costo or 0) > 0:
                    # Verificar si ya existe un registro para esta cita
                    existe = db.fetch_one("SELECT id FROM procedimientos_paciente WHERE cita_id = %s", (cita_id,))
                    if not existe:
                        db.execute_query("""
                            INSERT INTO procedimientos_paciente (paciente_id, cita_id, costo, estado, fecha_realizacion, notas)
                            VALUES (%s, %s, %s, 'completado', %s, %s)
                        """, (cita_actualizada.paciente_id, cita_id, cita_actualizada.costo, cita_actualizada.fecha_hora.date(), f"{cita_actualizada.tipo.upper()}: {cita_actualizada.procedimiento}"))
                    else:
                        db.execute_query("""
                            UPDATE procedimientos_paciente SET costo = %s, fecha_realizacion = %s, notas = %s, estado = 'completado', paciente_id = %s
                            WHERE cita_id = %s
                        """, (cita_actualizada.costo, cita_actualizada.fecha_hora.date(), f"{cita_actualizada.tipo.upper()}: {cita_actualizada.procedimiento}", cita_actualizada.paciente_id, cita_id))

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
                
                # Crear registro en procedimientos_paciente si tiene costo
                cita_data = db.fetch_one("SELECT paciente_id, costo, tipo, procedimiento, fecha_hora FROM citas WHERE id = %s", (cita_id,))
                if cita_data and float(cita_data[1] or 0) > 0:
                    paciente_id, costo, tipo, desc, fecha_hora = cita_data
                    # Verificar si ya existe un registro para esta cita
                    existe = db.fetch_one("SELECT id FROM procedimientos_paciente WHERE cita_id = %s", (cita_id,))
                    if not existe:
                        db.execute_query("""
                            INSERT INTO procedimientos_paciente (paciente_id, cita_id, costo, estado, fecha_realizacion, notas)
                            VALUES (%s, %s, %s, 'completado', %s, %s)
                        """, (paciente_id, cita_id, costo, fecha_hora.date(), f"{tipo.upper()}: {desc}"))
                    else:
                        db.execute_query("""
                            UPDATE procedimientos_paciente SET costo = %s, fecha_realizacion = %s, notas = %s, estado = 'completado'
                            WHERE cita_id = %s
                        """, (costo, fecha_hora.date(), f"{tipo.upper()}: {desc}", cita_id))

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