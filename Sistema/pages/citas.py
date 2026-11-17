from nicegui import app, ui

import database as db
import servicios_citas as sc
import validaciones as val
from components.cita_form import CitaForm
from components.confirmacion import confirmar
from components.paciente_selector import PacienteSelector
from models.cita import Cita


def puede_eliminar_usuario() -> bool:
    user = app.storage.user.get('user', {})
    permisos = user.get('permisos') if isinstance(user.get('permisos'), dict) else {}
    return bool(user.get('es_superadmin', False) or permisos.get('puede_eliminar', False))


SLOT_ACCIONES = '''
    <q-td :props="props">
        <q-btn flat round dense icon="edit" @click="$parent.$emit('edit', props.row.id)" v-if="['programada', 'en_curso'].includes(props.row.estado)">
            <q-tooltip>Editar</q-tooltip>
        </q-btn>
        <q-btn flat round dense icon="cancel" color="orange" @click="$parent.$emit('cancel', props.row.id)" v-if="['programada', 'en_curso'].includes(props.row.estado)">
            <q-tooltip>Cancelar cita</q-tooltip>
        </q-btn>
        <q-btn flat round dense icon="play_arrow" color="green" @click="$parent.$emit('start', props.row.id)" v-if="props.row.estado === 'programada'">
            <q-tooltip>Iniciar cita</q-tooltip>
        </q-btn>
        <q-btn flat round dense icon="check" color="green" @click="$parent.$emit('complete', props.row.id)" v-if="props.row.estado === 'en_curso'">
            <q-tooltip>Completar cita</q-tooltip>
        </q-btn>
        <q-btn flat round dense icon="delete" color="red" @click="$parent.$emit('delete', props.row.id)" v-if="props.row.can_delete">
            <q-tooltip>Eliminar</q-tooltip>
        </q-btn>
    </q-td>
'''

SLOT_ESTADO = '''
    <q-td :props="props">
        <q-badge :color="props.row.estado_color" rounded class="q-px-sm q-py-xs">
            {{ props.value.replace('_', ' ') }}
        </q-badge>
    </q-td>
'''


class AccionesCitas:
    """Acciones de la tabla de citas, compartidas con la Vista general."""

    def cargar_citas(self):
        raise NotImplementedError

    def configurar_tabla(self, tabla):
        tabla.add_slot('body-cell-estado', SLOT_ESTADO)
        tabla.add_slot('body-cell-acciones', SLOT_ACCIONES)
        tabla.on('edit', lambda e: self.editar_cita(e.args))
        tabla.on('cancel', lambda e: self.cancelar_cita(e.args))
        tabla.on('start', lambda e: self.iniciar_cita(e.args))
        tabla.on('complete', lambda e: self.completar_cita(e.args))
        tabla.on('delete', lambda e: self.eliminar_cita(e.args))

    def fila(self, cita_row: dict) -> dict:
        cita_row['estado_color'] = sc.COLORES_ESTADO.get(cita_row['estado'], 'grey')
        cita_row['tipo'] = sc.TIPOS_CITA.get(cita_row['tipo'], cita_row['tipo'])
        cita_row['procedimiento'] = cita_row.get('procedimiento') or ''
        cita_row['can_delete'] = self.puede_eliminar
        return cita_row

    def mostrar_form_nueva_cita(self, paciente_id=None):
        def guardar(cita):
            try:
                sc.crear_cita(cita)
                ui.notify('Cita guardada exitosamente', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar cita: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog().classes('w-full max-w-2xl') as dialog:
            CitaForm(cita=Cita(paciente_id=paciente_id) if paciente_id else None,
                     on_save=guardar, on_cancel=dialog.close)
        dialog.open()

    def editar_cita(self, cita_id):
        cita = sc.obtener_cita(cita_id)
        if not cita:
            ui.notify('Cita no encontrada', type='warning')
            return
        if cita.estado not in val.ESTADOS_CITA_ACTIVOS:
            ui.notify('Solo se pueden editar citas programadas o en curso (RN11)', type='warning')
            return

        def actualizar(cita_actualizada):
            try:
                sc.actualizar_cita(cita_actualizada)
                ui.notify('Cita actualizada', type='positive')
                self.cargar_citas()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog().classes('w-full max-w-2xl') as dialog:
            CitaForm(cita=cita, on_save=actualizar, on_cancel=dialog.close)
        dialog.open()

    def _cambiar_estado(self, cita_id, estado, mensaje_ok):
        try:
            if sc.cambiar_estado(cita_id, estado):
                ui.notify(mensaje_ok, type='positive')
            else:
                ui.notify('La cita ya no permite este cambio de estado', type='warning')
            self.cargar_citas()
        except Exception as e:
            ui.notify(f'Error: {val.mensaje_error_bd(e)}', type='negative')

    def iniciar_cita(self, cita_id):
        confirmar('¿Iniciar cita?', 'La cita cambiará a estado "en curso".',
                  lambda: self._cambiar_estado(cita_id, 'en_curso', 'Cita iniciada'),
                  texto_confirmar='Iniciar', color='green')

    def completar_cita(self, cita_id):
        confirmar('¿Completar cita?', 'La cita cambiará a estado "completada".',
                  lambda: self._cambiar_estado(cita_id, 'completada', 'Cita completada'),
                  texto_confirmar='Completar', color='green')

    def cancelar_cita(self, cita_id):
        confirmar('¿Cancelar cita?', 'La cita cambiará a estado "cancelada" y ya no podrá modificarse.',
                  lambda: self._cambiar_estado(cita_id, 'cancelada', 'Cita cancelada'),
                  texto_confirmar='Sí, cancelar', color='orange', texto_cancelar='No')

    def eliminar_cita(self, cita_id):
        if not self.puede_eliminar:
            ui.notify('No tiene permiso para eliminar', type='warning')
            return

        def eliminar():
            try:
                sc.eliminar_cita(cita_id)
                ui.notify('Cita eliminada', type='positive')
                self.cargar_citas()
            except Exception as e:
                ui.notify(f'Error al eliminar: {val.mensaje_error_bd(e)}', type='negative')

        confirmar('¿Eliminar cita permanentemente?', 'Esta acción no se puede deshacer.',
                  eliminar, texto_confirmar='Eliminar', color='red')


class CitasPage(AccionesCitas):
    def __init__(self):
        self.puede_eliminar = puede_eliminar_usuario()
        self.paciente_id = None
        self.paciente_nombre_filtro = 'Ningún paciente seleccionado'
        self.create_content()

    def create_content(self):
        ui.label('Gestión de Citas').classes('text-h4 mb-4')

        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector_filtro).props('outline color=primary')

            self.paciente_filtro_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
            with self.paciente_filtro_display:
                ui.icon('person', color='primary')
                self.label_paciente_filtro = ui.label(self.paciente_nombre_filtro).classes('font-bold')
                ui.button(icon='close', on_click=self.limpiar_filtro_paciente).props('flat dense color=grey')
            self.paciente_filtro_display.set_visibility(False)

            ui.space()
            ui.button('Nueva Cita', icon='add',
                      on_click=lambda: self.mostrar_form_nueva_cita(self.paciente_id)) \
                .props('flat color=primary')

        self.mensaje_sin_paciente = ui.label('Seleccione un paciente para ver su historial de citas.') \
            .classes('text-italic text-grey-7')

        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
            {'name': 'fecha_hora', 'label': 'Fecha y Hora', 'field': 'fecha_hora', 'sortable': True},
            {'name': 'paciente', 'label': 'Paciente', 'field': 'paciente', 'sortable': True},
            {'name': 'tipo', 'label': 'Tipo', 'field': 'tipo', 'sortable': True},
            {'name': 'procedimiento', 'label': 'Procedimiento', 'field': 'procedimiento'},
            {'name': 'doctor', 'label': 'Doctor', 'field': 'doctor'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'},
            {'name': 'acciones', 'label': 'Acciones', 'field': 'acciones'}
        ]
        self.citas_table = ui.table(columns=columns, rows=[], row_key='id', pagination=10).classes('w-full')
        self.configurar_tabla(self.citas_table)
        self.cargar_citas()

    def abrir_selector_filtro(self):
        PacienteSelector(on_select=self.aplicar_filtro_paciente).open()

    def aplicar_filtro_paciente(self, pid, name):
        self.paciente_id = pid
        self.label_paciente_filtro.set_text(name)
        self.paciente_filtro_display.set_visibility(True)
        self.cargar_citas()

    def limpiar_filtro_paciente(self):
        self.paciente_id = None
        self.label_paciente_filtro.set_text(self.paciente_nombre_filtro)
        self.paciente_filtro_display.set_visibility(False)
        self.cargar_citas()

    def cargar_citas(self):
        self.mensaje_sin_paciente.set_visibility(not self.paciente_id)
        if not self.paciente_id:
            self.citas_table.rows = []
            return

        citas = db.fetch_all("""
            SELECT c.id,
                   TO_CHAR(c.fecha_hora, 'DD/MM/YYYY HH24:MI'),
                   p.nombre || ' ' || p.apellidos,
                   c.tipo,
                   c.procedimiento,
                   COALESCE(u.nombre || CASE WHEN u.activo THEN '' ELSE ' (inactivo)' END, 'Sin asignar'),
                   c.estado
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            LEFT JOIN usuarios u ON c.doctor_id = u.id
            WHERE c.paciente_id = %s
            ORDER BY c.fecha_hora DESC
        """, (self.paciente_id,))

        self.citas_table.rows = [
            self.fila({'id': c[0], 'fecha_hora': c[1], 'paciente': c[2], 'tipo': c[3],
                       'procedimiento': c[4], 'doctor': c[5], 'estado': c[6]})
            for c in citas
        ]

    def refresh(self):
        self.cargar_citas()
