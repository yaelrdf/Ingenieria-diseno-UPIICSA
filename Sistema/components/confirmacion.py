from nicegui import ui


def confirmar(titulo: str, mensaje: str, on_confirm, texto_confirmar: str = 'Confirmar',
              color: str = 'primary', texto_cancelar: str = 'Cancelar'):
    """Diálogo de confirmación genérico; ejecuta on_confirm solo si el usuario acepta."""
    def aceptar():
        dialog.close()
        on_confirm()

    with ui.dialog() as dialog, ui.card():
        ui.label(titulo).classes('text-h6')
        ui.label(mensaje)
        with ui.row().classes('w-full justify-end'):
            ui.button(texto_cancelar, on_click=dialog.close).props('flat')
            ui.button(texto_confirmar, on_click=aceptar, color=color)
    dialog.open()
