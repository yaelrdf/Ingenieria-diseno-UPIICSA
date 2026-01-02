from nicegui import ui
import database as db

class PacienteSelector:
    def __init__(self, on_select, label="Seleccionar Paciente"):
        self.on_select = on_select
        self.label = label
        self.dialog = None
        self.search_input = None
        self.results_container = None
        
    def open(self):
        self.dialog = ui.dialog().classes('w-full max-w-lg')
        with self.dialog, ui.card().classes('w-full'):
            ui.label(self.label).classes('text-h6 mb-2')
            self.search_input = ui.input(
                placeholder='Nombre o teléfono...',
                on_change=self.buscar
            ).props('outlined autofocus clearable').classes('w-full mb-4')
            
            self.results_container = ui.column().classes('w-full gap-2 max-h-96 overflow-y-auto')
            self.buscar()
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cerrar', on_click=self.dialog.close).props('flat')
        
        self.dialog.open()
        
    def buscar(self):
        query = self.search_input.value if self.search_input else ""
        if not query:
            sql = "SELECT id, nombre || ' ' || apellidos, telefono FROM pacientes ORDER BY nombre LIMIT 10"
            params = ()
        else:
            search = f"%{query}%"
            sql = "SELECT id, nombre || ' ' || apellidos, telefono FROM pacientes WHERE nombre ILIKE %s OR apellidos ILIKE %s OR telefono ILIKE %s ORDER BY nombre LIMIT 20"
            params = (search, search, search)
            
        resultados = db.fetch_all(sql, params)
        
        self.results_container.clear()
        with self.results_container:
            if not resultados:
                ui.label('No se encontraron pacientes').classes('text-italic text-gray-500')
            for r in resultados:
                # Use a closure for lambda to capture current values
                def create_on_click(pid=r[0], pname=r[1]):
                    return lambda: self.seleccionar(pid, pname)
                
                with ui.card().classes('w-full cursor-pointer hover:bg-blue-50').on('click', create_on_click()):
                    with ui.row().classes('w-full items-center justify-between'):
                        with ui.column():
                            ui.label(r[1]).classes('font-bold')
                            ui.label(r[2] or 'Sin teléfono').classes('text-caption')
                        ui.icon('chevron_right')

    def seleccionar(self, paciente_id, nombre):
        if self.on_select:
            self.on_select(paciente_id, nombre)
        if self.dialog:
            self.dialog.close()
