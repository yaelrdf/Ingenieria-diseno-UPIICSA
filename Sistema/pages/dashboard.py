from datetime import date

from nicegui import app, ui

import database as db
from pages.citas import AccionesCitas, puede_eliminar_usuario


class DashboardPage(AccionesCitas):
    def __init__(self):
        user = app.storage.user.get('user', {})
        self.es_superadmin = user.get('es_superadmin', False)
        self.medico_id = user.get('medico_id')
        self.puede_eliminar = puede_eliminar_usuario()
        self.fecha_seleccionada = date.today()
        self.create_content()

    def create_content(self):
        ui.label('Vista general del dia').classes('text-4xl font-bold mb-6 mt-4').style('font-family: "Georgia", serif; font-style: italic;')

        with ui.dialog() as self.dialog_fecha:
            with ui.card():
                self.fecha_input = ui.date(value=self.fecha_seleccionada.isoformat(),
                                           on_change=self.on_date_change).props('outlined')

        with ui.row().classes('w-full items-center mb-6 gap-4'):
            with ui.row().classes('items-center gap-2 bg-[#f5f6fa] p-3 rounded-xl border border-gray-100 shadow-sm cursor-pointer').on('click', self.dialog_fecha.open):
                ui.icon('calendar_today', color='primary')
                self.label_fecha = ui.label(self.fecha_seleccionada.strftime('%d/%m/%Y')).classes('font-bold text-lg')
                ui.icon('arrow_drop_down', color='primary')

            ui.button('Hoy', on_click=self.set_fecha_hoy).props('flat color=primary').classes('rounded-lg')

        columns = [
            {'name': 'hora', 'label': 'Hora', 'field': 'hora', 'sortable': True, 'align': 'left'},
            {'name': 'paciente', 'label': 'Paciente', 'field': 'paciente', 'sortable': True, 'align': 'left'},
            {'name': 'tipo', 'label': 'Tipo', 'field': 'tipo', 'align': 'left'},
            {'name': 'procedimiento', 'label': 'Procedimiento', 'field': 'procedimiento', 'align': 'left'},
            {'name': 'doctor', 'label': 'Doctor', 'field': 'doctor', 'align': 'left'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado', 'align': 'center'},
            {'name': 'acciones', 'label': 'Acciones', 'field': 'acciones', 'align': 'right'}
        ]
        self.citas_table = ui.table(columns=columns, rows=[], row_key='id', pagination=10) \
            .classes('w-full shadow-md rounded-xl border border-gray-100')
        self.configurar_tabla(self.citas_table)
        self.cargar_citas()

    def set_fecha_hoy(self):
        self.fecha_input.value = date.today().isoformat()

    def on_date_change(self, e):
        self.dialog_fecha.close()
        if not self.fecha_input.value:
            return
        self.label_fecha.set_text(date.fromisoformat(self.fecha_input.value).strftime('%d/%m/%Y'))
        self.cargar_citas()

    def cargar_citas(self):
        query = """
        SELECT c.id,
               TO_CHAR(c.fecha_hora, 'HH24:MI'),
               p.nombre || ' ' || p.apellidos,
               c.tipo,
               c.procedimiento,
               COALESCE(u.nombre || CASE WHEN u.activo THEN '' ELSE ' (inactivo)' END, 'Sin asignar'),
               c.estado
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        LEFT JOIN usuarios u ON c.doctor_id = u.id
        WHERE c.fecha_hora::date = %s
        """
        params = [self.fecha_input.value]

        # Un médico ve sus citas y las que no tienen médico asignado (RN03)
        if not self.es_superadmin and self.medico_id:
            query += ' AND (c.doctor_id = %s OR c.doctor_id IS NULL)'
            params.append(self.medico_id)
        query += ' ORDER BY c.fecha_hora'

        self.citas_table.rows = [
            self.fila({'id': c[0], 'hora': c[1], 'paciente': c[2], 'tipo': c[3],
                       'procedimiento': c[4], 'doctor': c[5], 'estado': c[6]})
            for c in db.fetch_all(query, params)
        ]

    def refresh(self):
        self.cargar_citas()
