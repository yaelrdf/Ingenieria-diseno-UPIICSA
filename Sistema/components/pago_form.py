from nicegui import ui
from datetime import date
import database as db
from models.pago import Pago

class PagoForm:
    def __init__(self, procedimientos_pendientes=None, on_save=None, on_cancel=None):
        self.procedimientos_pendientes = procedimientos_pendientes or []
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.create_form()
    
    def create_form(self):
        with ui.card().classes('w-full'):
            ui.label('Registrar Pago').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4'):
                # Selector de procedimiento
                if self.procedimientos_pendientes:
                    opciones = {}
                    for proc in self.procedimientos_pendientes:
                        opciones[proc[0]] = f"{proc[1]} - Pendiente: ${proc[2]:,.2f}"
                    
                    self.select_procedimiento = ui.select(
                        label='Procedimiento',
                        options=opciones,
                        value=self.procedimientos_pendientes[0][0] if self.procedimientos_pendientes else None
                    ).props('outlined').classes('w-full')
                else:
                    ui.label('No hay procedimientos pendientes de pago').classes('text-italic')
                    self.select_procedimiento = None
                
                # Monto
                self.input_monto = ui.number(
                    'Monto',
                    value=0.0,
                    format='%.2f',
                    prefix='$'
                ).props('outlined').classes('w-full')
                
                # Método de pago
                self.select_metodo = ui.select(
                    label='Método de Pago',
                    options={
                        'efectivo': 'Efectivo',
                        'tarjeta_credito': 'Tarjeta de Crédito',
                        'tarjeta_debito': 'Tarjeta de Débito',
                        'transferencia': 'Transferencia',
                        'cheque': 'Cheque'
                    },
                    value='efectivo'
                ).props('outlined').classes('w-full')
                
                # Fecha de pago
                ui.label('Fecha de Pago')
                self.input_fecha = ui.date(value=date.today()).props('outlined').classes('w-full')
                
                # Concepto
                self.input_concepto = ui.input(
                    'Concepto',
                    placeholder='Ej: Pago parcial de endodoncia'
                ).props('outlined').classes('w-full')
                
                # Notas
                self.textarea_notas = ui.textarea(
                    'Notas',
                    placeholder='Observaciones adicionales...'
                ).props('outlined rows=3').classes('w-full')
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancelar', on_click=self.on_cancel).props('flat')
                ui.button('Registrar', on_click=self.guardar, icon='payments').props('flat color=primary')
    
    def guardar(self):
        if not self.select_procedimiento:
            ui.notify('No hay procedimientos disponibles', type='warning')
            return
        
        monto = self.input_monto.value
        if not monto or monto <= 0:
            ui.notify('Ingrese un monto válido', type='warning')
            return
        
        fecha_val = self.input_fecha.value
        try:
            if isinstance(fecha_val, str):
                fecha_pago = date.fromisoformat(fecha_val) if fecha_val else date.today()
            else:
                fecha_pago = fecha_val or date.today()
        except (ValueError, TypeError):
            fecha_pago = date.today()
            
        pago = Pago(
            procedimiento_id=self.select_procedimiento.value,
            monto=float(monto),
            metodo_pago=self.select_metodo.value,
            fecha_pago=fecha_pago,
            concepto=self.input_concepto.value or f"Pago - {fecha_pago.strftime('%d/%m/%Y')}",
            notas=self.textarea_notas.value
        )
        
        if self.on_save:
            self.on_save(pago)