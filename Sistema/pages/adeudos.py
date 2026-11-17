from nicegui import ui

import database as db
import validaciones as val
from components.paciente_selector import PacienteSelector
from components.pago_form import METODOS_PAGO, PagoForm

# Nombre visible del procedimiento: catálogo, descripción de la cita o tipo de cita
NOMBRE_PROCEDIMIENTO = """COALESCE(pr.nombre, NULLIF(c.procedimiento, ''), INITCAP(c.tipo),
                                    NULLIF(pp.notas, ''), 'Procedimiento #' || pp.id)"""

# Saldo pendiente por procedimiento (completados y en proceso)
SQL_SALDOS = f"""
    SELECT pp.id, {NOMBRE_PROCEDIMIENTO} AS nombre, pp.fecha_realizacion, pp.costo,
           COALESCE(pg.pagado, 0) AS pagado, pp.costo - COALESCE(pg.pagado, 0) AS pendiente, pp.estado
    FROM procedimientos_paciente pp
    LEFT JOIN procedimientos pr ON pp.procedimiento_id = pr.id
    LEFT JOIN citas c ON pp.cita_id = c.id
    LEFT JOIN (SELECT procedimiento_id, SUM(monto) AS pagado FROM pagos GROUP BY procedimiento_id) pg
           ON pg.procedimiento_id = pp.id
    WHERE pp.paciente_id = %s AND pp.estado IN ('completado', 'en_proceso')
      AND pp.costo - COALESCE(pg.pagado, 0) > 0
"""


class AdeudosPage:
    def __init__(self):
        self.paciente_id = None
        self.create_content()

    def create_content(self):
        ui.label('Gestión de Adeudos y Pagos').classes('text-h4 mb-4')

        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector).props('outline color=primary')
            self.paciente_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
            with self.paciente_display:
                ui.icon('person', color='primary')
                self.label_paciente = ui.label('Seleccione un paciente').classes('font-bold')
            self.paciente_display.set_visibility(False)

        with ui.card().classes('w-full mb-4'):
            ui.label('Resumen Financiero').classes('text-h6 mb-2')
            with ui.grid(columns=3).classes('w-full gap-4'):
                with ui.card().classes('text-center'):
                    ui.label('Adeudo Total').classes('text-subtitle2')
                    self.label_total = ui.label('$0.00').classes('text-h5 text-red')
                with ui.card().classes('text-center'):
                    ui.label('Total Pagado').classes('text-subtitle2')
                    self.label_pagado = ui.label('$0.00').classes('text-h5 text-green')
                with ui.card().classes('text-center'):
                    ui.label('Saldo Pendiente').classes('text-subtitle2')
                    self.label_saldo = ui.label('$0.00').classes('text-h5 text-orange')
            ui.label('Solo los procedimientos completados generan adeudo y pueden pagarse (RN02).') \
                .classes('text-caption text-grey-7 mt-2')

        with ui.row().classes('w-full justify-end mb-4'):
            ui.button('Registrar Pago', on_click=self.mostrar_form_pago, icon='payments') \
                .props('flat color=primary').bind_enabled_from(self, 'paciente_id', backward=bool)

        ui.label('Procedimientos con saldo').classes('text-h6')
        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'procedimiento', 'label': 'Procedimiento', 'field': 'procedimiento', 'align': 'left'},
            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha'},
            {'name': 'costo', 'label': 'Costo', 'field': 'costo'},
            {'name': 'pagado', 'label': 'Pagado', 'field': 'pagado'},
            {'name': 'pendiente', 'label': 'Pendiente', 'field': 'pendiente'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'}
        ]
        self.procedimientos_table = ui.table(columns=columns, rows=[], row_key='id').classes('w-full')
        self.procedimientos_table.add_slot('body-cell-estado', '''
            <q-td :props="props">
                <q-badge :color="props.row.estado_color">{{ props.value }}</q-badge>
            </q-td>
        ''')

        ui.label('Historial de Pagos').classes('text-h6 mt-4')
        columns_pagos = [
            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha'},
            {'name': 'concepto', 'label': 'Concepto', 'field': 'concepto', 'align': 'left'},
            {'name': 'procedimiento', 'label': 'Procedimiento', 'field': 'procedimiento', 'align': 'left'},
            {'name': 'monto', 'label': 'Monto', 'field': 'monto'},
            {'name': 'metodo', 'label': 'Método', 'field': 'metodo'},
            {'name': 'notas', 'label': 'Notas', 'field': 'notas', 'align': 'left'}
        ]
        self.pagos_table = ui.table(columns=columns_pagos, rows=[], row_key='id', pagination=10).classes('w-full')

    def abrir_selector(self):
        PacienteSelector(on_select=self.seleccionar_paciente).open()

    def seleccionar_paciente(self, pid, name):
        self.paciente_id = pid
        self.label_paciente.set_text(name)
        self.paciente_display.set_visibility(True)
        self.cargar_adeudos()

    def cargar_adeudos(self):
        if not self.paciente_id:
            return
        self.cargar_resumen_financiero()
        self.cargar_detalle_procedimientos()
        self.cargar_historial_pagos()

    def cargar_resumen_financiero(self):
        total_adeudo, total_pagado = db.fetch_one("""
            SELECT
                (SELECT COALESCE(SUM(costo), 0) FROM procedimientos_paciente
                 WHERE paciente_id = %s AND estado = 'completado'),
                (SELECT COALESCE(SUM(monto), 0) FROM pagos WHERE paciente_id = %s)
        """, (self.paciente_id, self.paciente_id))
        total_adeudo = float(total_adeudo)
        total_pagado = float(total_pagado)
        self.label_total.set_text(f'${total_adeudo:,.2f}')
        self.label_pagado.set_text(f'${total_pagado:,.2f}')
        self.label_saldo.set_text(f'${max(total_adeudo - total_pagado, 0):,.2f}')

    def cargar_detalle_procedimientos(self):
        filas = db.fetch_all(SQL_SALDOS + ' ORDER BY pp.fecha_realizacion DESC NULLS LAST, pp.id DESC',
                             (self.paciente_id,))
        self.procedimientos_table.rows = [{
            'id': f[0],
            'procedimiento': f[1],
            'fecha': f[2].strftime('%d/%m/%Y') if f[2] else 'N/A',
            'costo': f'${f[3]:,.2f}',
            'pagado': f'${f[4]:,.2f}',
            'pendiente': f'${f[5]:,.2f}',
            'estado': 'pendiente de pago' if f[6] == 'completado' else 'en proceso (no pagable)',
            'estado_color': 'orange' if f[6] == 'completado' else 'grey',
        } for f in filas]

    def cargar_historial_pagos(self):
        pagos = db.fetch_all(f"""
            SELECT p.id, p.fecha_pago, p.concepto, p.monto, p.metodo_pago, p.notas,
                   CASE WHEN pp.id IS NULL THEN NULL ELSE {NOMBRE_PROCEDIMIENTO} END
            FROM pagos p
            LEFT JOIN procedimientos_paciente pp ON p.procedimiento_id = pp.id
            LEFT JOIN procedimientos pr ON pp.procedimiento_id = pr.id
            LEFT JOIN citas c ON pp.cita_id = c.id
            WHERE p.paciente_id = %s
            ORDER BY p.fecha_pago DESC, p.created_at DESC
        """, (self.paciente_id,))
        self.pagos_table.rows = [{
            'id': p[0],
            'fecha': p[1].strftime('%d/%m/%Y'),
            'concepto': p[2] or '',
            'procedimiento': p[6] or 'N/A',
            'monto': f'${p[3]:,.2f}',
            'metodo': METODOS_PAGO.get(p[4], (p[4] or 'No especificado').replace('_', ' ').capitalize()),
            'notas': p[5] or ''
        } for p in pagos]

    def procedimientos_pagables(self):
        """Solo procedimientos 'completado' con saldo (RN02); los 'en_proceso' no se pueden pagar."""
        return [(f[0], f[1], f[5]) for f in db.fetch_all(SQL_SALDOS + " AND pp.estado = 'completado' ORDER BY pp.id",
                                                         (self.paciente_id,))]

    def mostrar_form_pago(self):
        if not self.paciente_id:
            ui.notify('Seleccione un paciente primero', type='warning')
            return

        def guardar_pago(pago):
            # Revalidación contra la BD al momento de guardar (estado y saldo actuales)
            vigentes = {p[0]: float(p[2]) for p in self.procedimientos_pagables()}
            if pago.procedimiento_id not in vigentes:
                ui.notify('El procedimiento ya no tiene saldo pendiente o no está completado', type='warning')
                return
            if pago.monto > round(vigentes[pago.procedimiento_id], 2):
                ui.notify(f'El monto excede el saldo pendiente (${vigentes[pago.procedimiento_id]:,.2f})', type='warning')
                return
            try:
                db.execute_query("""
                    INSERT INTO pagos (paciente_id, procedimiento_id, monto, metodo_pago, fecha_pago, concepto, notas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.paciente_id, pago.procedimiento_id, pago.monto, pago.metodo_pago,
                      pago.fecha_pago, pago.concepto, pago.notas))
                ui.notify('Pago registrado exitosamente', type='positive')
                self.cargar_adeudos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al registrar pago: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog().classes('w-full max-w-md') as dialog:
            PagoForm(procedimientos_pendientes=self.procedimientos_pagables(),
                     on_save=guardar_pago, on_cancel=dialog.close)
        dialog.open()
