from nicegui import ui
import database as db
from models.pago import Pago
from components.pago_form import PagoForm
from components.paciente_selector import PacienteSelector

class AdeudosPage:
    def __init__(self):
        self.paciente_id = None
        self.total_adeudo = 0.0
        self.total_pagado = 0.0
        self.saldo_pendiente = 0.0
        self.create_content()
    
    def create_content(self):
        ui.label('Gestión de Adeudos y Pagos').classes('text-h4 mb-4')
        
        # Selector de paciente
        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector).props('outline color=primary')
            
            self.paciente_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
            with self.paciente_display:
                ui.icon('person', color='primary')
                self.label_paciente = ui.label('Seleccione un paciente').classes('font-bold')
            
            self.paciente_display.set_visibility(self.paciente_id is not None)
        
        # Resumen financiero
        with ui.card().classes('w-full mb-4'):
            ui.label('Resumen Financiero').classes('text-h6 mb-2')
            
            with ui.grid(columns=3).classes('w-full gap-4'):
                self.card_total = ui.card().classes('text-center')
                with self.card_total:
                    ui.label('Total Adeudo').classes('text-subtitle2')
                    self.label_total = ui.label('$0.00').classes('text-h5 text-red')
                
                self.card_pagado = ui.card().classes('text-center')
                with self.card_pagado:
                    ui.label('Total Pagado').classes('text-subtitle2')
                    self.label_pagado = ui.label('$0.00').classes('text-h5 text-green')
                
                self.card_saldo = ui.card().classes('text-center')
                with self.card_saldo:
                    ui.label('Saldo Pendiente').classes('text-subtitle2')
                    self.label_saldo = ui.label('$0.00').classes('text-h5 text-orange')
        
        # Botón para agregar pago
        with ui.row().classes('w-full justify-end mb-4'):
            ui.button('+ Registrar Pago', on_click=self.mostrar_form_pago, 
                     icon='payments').props('flat color=primary').bind_enabled_from(self, 'paciente_id')
        
        # Tabla de procedimientos con adeudo
        ui.label('Detalle de Procedimientos').classes('text-h6')
        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'procedimiento', 'label': 'Procedimiento', 'field': 'procedimiento'},
            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha'},
            {'name': 'costo', 'label': 'Costo', 'field': 'costo'},
            {'name': 'pagado', 'label': 'Pagado', 'field': 'pagado'},
            {'name': 'pendiente', 'label': 'Pendiente', 'field': 'pendiente'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'}
        ]
        
        self.procedimientos_table = ui.table(
            columns=columns,
            rows=[],
            row_key='id'
        ).classes('w-full')
        
        self.procedimientos_table.add_slot('body-cell-estado', '''
            <q-td :props="props">
                <q-badge :color="props.value === 'pagado' ? 'green' : 'orange'">
                    {{ props.value }}
                </q-badge>
            </q-td>
        ''')
        
        # Tabla de movimientos de pagos
        ui.label('Historial de Pagos').classes('text-h6 mt-4')
        columns_pagos = [
            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha'},
            {'name': 'concepto', 'label': 'Concepto', 'field': 'concepto'},
            {'name': 'monto', 'label': 'Monto', 'field': 'monto'},
            {'name': 'metodo', 'label': 'Método', 'field': 'metodo'},
            {'name': 'notas', 'label': 'Notas', 'field': 'notas'}
        ]
        
        self.pagos_table = ui.table(
            columns=columns_pagos,
            rows=[],
            row_key='id',
            pagination=10
        ).classes('w-full')
        
        # Inicialmente vacío
        self.mostrar_vacio()
    
    def abrir_selector(self):
        PacienteSelector(on_select=self.seleccionar_paciente).open()
        
    def seleccionar_paciente(self, pid, name):
        self.paciente_id = pid
        self.label_paciente.set_text(name)
        self.paciente_display.set_visibility(True)
        self.cargar_adeudos()

    def mostrar_vacio(self):
        self.label_total.set_text('$0.00')
        self.label_pagado.set_text('$0.00')
        self.label_saldo.set_text('$0.00')
        self.procedimientos_table.rows = []
        self.pagos_table.rows = []
    
    def cargar_adeudos(self):
        if not self.paciente_id:
            self.mostrar_vacio()
            return
        
        self.cargar_resumen_financiero()
        self.cargar_detalle_procedimientos()
        self.cargar_historial_pagos()
    
    def cargar_resumen_financiero(self):
        query = """
        SELECT 
            (SELECT COALESCE(SUM(costo), 0) FROM procedimientos_paciente 
             WHERE paciente_id = %s AND estado IN ('completado', 'en_proceso')) as total_adeudo,
            (SELECT COALESCE(SUM(monto), 0) FROM pagos 
             WHERE paciente_id = %s) as total_pagado
        """
        
        result = db.fetch_one(query, (self.paciente_id, self.paciente_id))
        
        if result:
            self.total_adeudo = float(result[0] or 0)
            self.total_pagado = float(result[1] or 0)
            self.saldo_pendiente = self.total_adeudo - self.total_pagado
            
            self.label_total.set_text(f"${self.total_adeudo:,.2f}")
            self.label_pagado.set_text(f"${self.total_pagado:,.2f}")
            self.label_saldo.set_text(f"${self.saldo_pendiente:,.2f}")
    
    def cargar_detalle_procedimientos(self):
        query = """
        SELECT pp.id, pr.nombre, pp.fecha_realizacion, pp.costo,
               COALESCE(SUM(pg.monto), 0) as pagado,
               pp.costo - COALESCE(SUM(pg.monto), 0) as pendiente,
               CASE 
                   WHEN pp.costo - COALESCE(SUM(pg.monto), 0) <= 0 THEN 'pagado'
                   ELSE 'pendiente'
               END as estado_pago
        FROM procedimientos_paciente pp
        LEFT JOIN procedimientos pr ON pp.procedimiento_id = pr.id
        LEFT JOIN pagos pg ON pp.id = pg.procedimiento_id
        WHERE pp.paciente_id = %s AND pp.estado IN ('completado', 'en_proceso')
        GROUP BY pp.id, pr.nombre, pp.fecha_realizacion, pp.costo
        HAVING pp.costo - COALESCE(SUM(pg.monto), 0) > 0
        ORDER BY pp.fecha_realizacion DESC
        """
        
        procedimientos = db.fetch_all(query, (self.paciente_id,))
        
        rows = []
        for proc in procedimientos:
            rows.append({
                'id': proc[0],
                'procedimiento': proc[1],
                'fecha': proc[2].strftime('%d/%m/%Y') if proc[2] else 'N/A',
                'costo': f"${proc[3]:,.2f}",
                'pagado': f"${proc[4]:,.2f}",
                'pendiente': f"${proc[5]:,.2f}",
                'estado': proc[6]
            })
        
        self.procedimientos_table.rows = rows
    
    def cargar_historial_pagos(self):
        query = """
        SELECT p.id, p.fecha_pago, p.concepto, p.monto, p.metodo_pago, p.notas
        FROM pagos p
        WHERE p.paciente_id = %s
        ORDER BY p.fecha_pago DESC, p.created_at DESC
        """
        
        pagos = db.fetch_all(query, (self.paciente_id,))
        
        rows = []
        for pago in pagos:
            rows.append({
                'id': pago[0],
                'fecha': pago[1].strftime('%d/%m/%Y'),
                'concepto': pago[2],
                'monto': f"${pago[3]:,.2f}",
                'metodo': pago[4].title() if pago[4] else 'No especificado',
                'notas': pago[5] or ''
            })
        
        self.pagos_table.rows = rows
    
    def mostrar_form_pago(self):
        if not self.paciente_id:
            ui.notify('Seleccione un paciente primero', type='warning')
            return
        
        def guardar_pago(pago):
            query = """
            INSERT INTO pagos (paciente_id, procedimiento_id, monto, 
                             metodo_pago, concepto, notas)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            params = (
                self.paciente_id,
                pago.procedimiento_id,
                pago.monto,
                pago.metodo_pago,
                pago.concepto,
                pago.notas
            )
            
            try:
                db.execute_query(query, params)
                ui.notify('Pago registrado exitosamente', type='positive')
                self.cargar_adeudos()
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al registrar pago: {str(e)}', type='negative')
        
        # Obtener procedimientos pendientes de pago
        query = """
        SELECT pp.id, pr.nombre, pp.costo - COALESCE(SUM(pg.monto), 0) as pendiente
        FROM procedimientos_paciente pp
        LEFT JOIN procedimientos pr ON pp.procedimiento_id = pr.id
        LEFT JOIN pagos pg ON pp.id = pg.procedimiento_id
        WHERE pp.paciente_id = %s AND pp.estado IN ('completado', 'en_proceso')
        GROUP BY pp.id, pr.nombre, pp.costo
        HAVING pp.costo - COALESCE(SUM(pg.monto), 0) > 0
        """
        
        procedimientos_pendientes = db.fetch_all(query, (self.paciente_id,))
        
        dialog = ui.dialog().classes('w-full max-w-md')
        with dialog:
            PagoForm(
                procedimientos_pendientes=procedimientos_pendientes,
                on_save=guardar_pago,
                on_cancel=dialog.close
            )
        dialog.open()