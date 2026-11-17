from datetime import date

from nicegui import ui

import validaciones as val
from models.pago import Pago

METODOS_PAGO = {
    'efectivo': 'Efectivo',
    'tarjeta_credito': 'Tarjeta de Crédito',
    'tarjeta_debito': 'Tarjeta de Débito',
    'transferencia': 'Transferencia',
    'cheque': 'Cheque',
}


class PagoForm:
    def __init__(self, procedimientos_pendientes=None, on_save=None, on_cancel=None):
        # Cada elemento: (id, nombre, saldo_pendiente)
        self.procedimientos_pendientes = procedimientos_pendientes or []
        self.saldos = {p[0]: float(p[2]) for p in self.procedimientos_pendientes}
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()

    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Registrar Pago').classes('text-h6 mb-4')

            with ui.column().classes('w-full gap-4'):
                if self.procedimientos_pendientes:
                    opciones = {p[0]: f'{p[1]} - Pendiente: ${float(p[2]):,.2f}' for p in self.procedimientos_pendientes}
                    # Un solo procedimiento por pago (RN08), sin valor preseleccionado
                    self.select_procedimiento = ui.select(
                        label='Procedimiento *',
                        options=opciones,
                        value=None,
                        validation={'Seleccione el procedimiento a pagar': lambda v: v is not None},
                    ).props('outlined').classes('w-full')
                else:
                    ui.label('No hay procedimientos completados con saldo pendiente').classes('text-italic')
                    self.select_procedimiento = None

                self.input_monto = ui.number('Monto *', value=None, format='%.2f', prefix='$', min=0) \
                    .props('outlined').classes('w-full')

                # Sin método por defecto: debe elegirse explícitamente (RF23, TC-80)
                self.select_metodo = ui.select(
                    label='Método de Pago *',
                    options=METODOS_PAGO,
                    value=None,
                    validation={'Seleccione el método de pago': lambda v: v is not None},
                ).props('outlined clearable').classes('w-full')

                # Fecha editable y que se puede vaciar (TC-79); se valida al guardar
                self.input_fecha = ui.date_input('Fecha de Pago *', value=date.today().isoformat()) \
                    .props('outlined clearable').classes('w-full')

                self.input_concepto = ui.input('Concepto', placeholder='Ej: Pago parcial de endodoncia') \
                    .props('outlined').classes('w-full')
                self.textarea_notas = ui.textarea('Notas', placeholder='Observaciones adicionales...') \
                    .props('outlined rows=3').classes('w-full')

            ui.label('* Campos obligatorios').classes('text-caption text-grey-7')
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Registrar', on_click=self.guardar, icon='payments').props('flat color=primary')

    def guardar(self):
        if not self.select_procedimiento:
            ui.notify('No hay procedimientos disponibles para pago', type='warning')
            return
        if not self.select_procedimiento.validate():
            ui.notify('El procedimiento es obligatorio', type='warning')
            return

        monto = self.input_monto.value
        if monto is None or monto == '':
            ui.notify('El monto es obligatorio', type='warning')
            return
        try:
            monto = round(float(monto), 2)
        except (ValueError, TypeError):
            ui.notify('El monto debe ser un valor numérico', type='warning')
            return
        if monto <= 0:
            ui.notify('El monto debe ser mayor a cero', type='warning')
            return
        saldo = self.saldos.get(self.select_procedimiento.value, 0)
        if monto > round(saldo, 2):
            ui.notify(f'El monto excede el saldo pendiente (${saldo:,.2f})', type='warning')
            return

        if not self.select_metodo.validate():
            ui.notify('El método de pago es obligatorio', type='warning')
            return

        if not self.input_fecha.value:
            ui.notify('La fecha de pago es obligatoria', type='warning')
            return
        try:
            fecha_pago = val.parse_fecha(self.input_fecha.value)
        except (ValueError, TypeError):
            ui.notify('La fecha de pago no es válida (formato AAAA-MM-DD)', type='warning')
            return
        if fecha_pago > date.today():
            ui.notify('La fecha de pago no puede ser futura', type='warning')
            return

        pago = Pago(
            procedimiento_id=self.select_procedimiento.value,
            monto=monto,
            metodo_pago=self.select_metodo.value,
            fecha_pago=fecha_pago,
            concepto=val.texto(self.input_concepto.value) or f"Pago - {fecha_pago.strftime('%d/%m/%Y')}",
            notas=self.textarea_notas.value
        )

        if self.on_save:
            self.on_save(pago)
