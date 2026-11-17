from nicegui import ui

import database as db
import servicios_citas as sc
import validaciones as val
from components.confirmacion import confirmar
from components.usuario_form import UsuarioForm
from models.usuario import Usuario
from pages.citas import puede_eliminar_usuario


class MedicosPage:
    def __init__(self):
        self.puede_eliminar = puede_eliminar_usuario()
        self.medicos_container = None
        self.create_content()

    def create_content(self):
        ui.label('Gestión de Médicos').classes('text-h4 mb-4')

        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Nuevo Médico', on_click=self.mostrar_form_nuevo, icon='person_add').props('flat color=primary')
            self.search_input = ui.input(placeholder='Buscar por nombre, email o teléfono...',
                                         on_change=self.cargar_medicos).props('outlined dense clearable').classes('flex-grow')
            with self.search_input:
                ui.icon('search')

        self.medicos_container = ui.column().classes('w-full gap-3')
        self.cargar_medicos()

    def cargar_medicos(self):
        search_term = val.texto(self.search_input.value)
        sql = 'SELECT id, nombre, email, telefono, especialidad, activo FROM usuarios'
        params = []
        if search_term:
            sql += ' WHERE nombre ILIKE %s OR email ILIKE %s OR telefono ILIKE %s'
            term = f'%{search_term}%'
            params = [term, term, term]
        sql += ' ORDER BY nombre'
        resultados = db.fetch_all(sql, params)

        self.medicos_container.clear()
        with self.medicos_container:
            if not resultados:
                ui.label('No se encontraron médicos' if search_term else 'No hay médicos registrados') \
                    .classes('text-subtitle2 italic text-gray-500')
                return
            for m in resultados:
                self.crear_tarjeta_medico(m)

    def crear_tarjeta_medico(self, data):
        medico_id, nombre, email, telefono, especialidad, activo = data

        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-start'):
                with ui.column().classes('flex-grow'):
                    with ui.row().classes('items-center gap-2'):
                        ui.label(nombre).classes('text-h6 font-bold')
                        if not activo:
                            ui.badge('Inactivo', color='red').props('rounded')

                    with ui.row().classes('gap-8'):
                        with ui.column().classes('gap-1'):
                            ui.label('Especialidad').classes('text-caption text-gray-600')
                            ui.label(val.mostrar(especialidad)).classes('text-body2')
                        with ui.column().classes('gap-1'):
                            ui.label('Teléfono').classes('text-caption text-gray-600')
                            ui.label(val.mostrar(telefono)).classes('text-body2')
                        with ui.column().classes('gap-1'):
                            ui.label('Email').classes('text-caption text-gray-600')
                            ui.label(email).classes('text-body2 break-all')

                with ui.column().classes('items-end gap-2'):
                    with ui.row().classes('gap-2'):
                        ui.button(icon='edit', on_click=lambda id=medico_id: self.editar_medico(id)).props('flat').tooltip('Editar')
                        ui.button(icon='event', on_click=lambda id=medico_id: self.ver_citas(id)).props('flat color=blue').tooltip('Ver Citas')
                        if self.puede_eliminar:
                            ui.button(icon='delete', on_click=lambda id=medico_id, n=nombre: self.eliminar_medico(id, n)) \
                                .props('flat color=red').tooltip('Eliminar')

    def mostrar_form_nuevo(self):
        def guardar_medico(usuario):
            try:
                db.execute_query("""
                    INSERT INTO usuarios (nombre, email, telefono, especialidad, activo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (usuario.nombre, usuario.email, usuario.telefono, usuario.especialidad, usuario.activo))
                ui.notify('Médico guardado exitosamente', type='positive')
                self.cargar_medicos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog().classes('w-full max-w-md') as dialog:
            UsuarioForm(on_save=guardar_medico, on_cancel=dialog.close)
        dialog.open()

    def editar_medico(self, medico_id):
        data = db.fetch_one('SELECT id, nombre, email, telefono, especialidad, activo FROM usuarios WHERE id = %s', (medico_id,))
        if not data:
            ui.notify('Médico no encontrado', type='warning')
            return
        usuario = Usuario(id=data[0], nombre=data[1], email=data[2], telefono=data[3], especialidad=data[4], activo=data[5])

        def actualizar_medico(u):
            # No se puede desactivar un médico con citas pendientes de atender
            if usuario.activo and not u.activo:
                pendientes = val.contar_citas_medico(u.id, solo_activas=True)
                if pendientes:
                    ui.notify(f'No se puede desactivar: el médico tiene {pendientes} cita(s) programada(s) o en curso. '
                              'Reasígnelas o cancélelas primero.', type='warning', multi_line=True)
                    return
            try:
                db.execute_query("""
                    UPDATE usuarios SET nombre=%s, email=%s, telefono=%s, especialidad=%s, activo=%s
                    WHERE id=%s
                """, (u.nombre, u.email, u.telefono, u.especialidad, u.activo, u.id))
                ui.notify('Médico actualizado exitosamente', type='positive')
                self.cargar_medicos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog().classes('w-full max-w-md') as dialog:
            UsuarioForm(usuario=usuario, on_save=actualizar_medico, on_cancel=dialog.close)
        dialog.open()

    def eliminar_medico(self, medico_id, nombre):
        # Integridad referencial: un médico con citas no se elimina (TC-48)
        total_citas = val.contar_citas_medico(medico_id)
        if total_citas:
            ui.notify(f'No se puede eliminar a {nombre}: tiene {total_citas} cita(s) registradas. '
                      'Si ya no labora en la clínica, desactívelo desde "Editar".',
                      type='warning', multi_line=True)
            return

        def eliminar():
            try:
                db.execute_query('DELETE FROM usuarios WHERE id = %s', (medico_id,))
                ui.notify('Médico eliminado', type='positive')
                self.cargar_medicos()
            except Exception as e:
                ui.notify(f'Error al eliminar: {val.mensaje_error_bd(e)}', type='negative')

        confirmar('¿Eliminar médico?', f'Se eliminará a {nombre}. Esta acción no se puede deshacer.',
                  eliminar, texto_confirmar='Eliminar', color='red')

    def ver_citas(self, medico_id):
        fila = db.fetch_one('SELECT nombre FROM usuarios WHERE id = %s', (medico_id,))
        if not fila:
            ui.notify('Médico no encontrado', type='warning')
            return

        citas = db.fetch_all("""
            SELECT TO_CHAR(c.fecha_hora, 'DD/MM/YYYY'), TO_CHAR(c.fecha_hora, 'HH24:MI'),
                   p.nombre || ' ' || p.apellidos, c.tipo, c.estado
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            WHERE c.doctor_id = %s
            ORDER BY c.fecha_hora DESC
        """, (medico_id,))
        rows = [{'fecha': c[0], 'hora': c[1], 'paciente': c[2],
                 'tipo': sc.TIPOS_CITA.get(c[3], c[3]), 'estado': sc.ESTADOS_CITA.get(c[4], c[4])}
                for c in citas]
        columns = [
            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha', 'sortable': True},
            {'name': 'hora', 'label': 'Hora', 'field': 'hora', 'sortable': True},
            {'name': 'paciente', 'label': 'Paciente', 'field': 'paciente', 'sortable': True},
            {'name': 'tipo', 'label': 'Tipo', 'field': 'tipo'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'}
        ]

        with ui.dialog().classes('w-full max-w-4xl') as dialog, ui.card().classes('w-full'):
            ui.label(f'Citas de {fila[0]}').classes('text-h6 mb-4')
            ui.table(columns=columns, rows=rows, pagination=10).classes('w-full')
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cerrar', on_click=dialog.close).props('flat')
        dialog.open()
