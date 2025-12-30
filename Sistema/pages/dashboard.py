from nicegui import ui
from datetime import datetime, timedelta
import database as db

class DashboardPage:
    def __init__(self):
        self.create_content()
    
    def crear_item_lista(self, inicial, titulo, subtitulo):
        """Crea un item de lista estilizado como en el mockup"""
        with ui.row().classes('w-full items-center p-4 mb-3 bg-[#f5f6fa] rounded-xl border border-gray-100 shadow-sm'):
            # Círculo con inicial
            with ui.element('div').classes('w-12 h-12 rounded-full bg-[#e8eaf6] flex items-center justify-center mr-4 shadow-inner'):
                ui.label(inicial).classes('text-[#5c6bc0] font-bold text-xl')
            
            # Texto
            with ui.column().classes('gap-0'):
                ui.label(titulo).classes('font-bold text-lg text-[#333]')
                ui.label(subtitulo).classes('text-gray-500 text-sm')

    def create_content(self):
        # Header "Proximas citas"
        ui.label('Proximas citas').classes('text-4xl font-bold mb-6 mt-4').style('font-family: "Georgia", serif; font-style: italic;')
        ui.separator().classes('mb-6 opacity-50')
        
        self.proximas_citas_container = ui.column().classes('w-full mb-12')
        self.load_proximas_citas()
        
        # Header "Atencion en curso"
        ui.label('Atencion en curso').classes('text-4xl font-bold mb-6 mt-8').style('font-family: "Georgia", serif; font-style: italic;')
        ui.separator().classes('mb-6 opacity-50')
        
        self.citas_atencion_container = ui.column().classes('w-full')
        self.load_citas_atencion()

    def load_proximas_citas(self):
        query = """
        SELECT c.id, p.nombre, c.procedimiento, c.fecha_hora
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        WHERE c.estado = 'programada'
        AND c.fecha_hora >= CURRENT_TIMESTAMP
        ORDER BY c.fecha_hora
        LIMIT 3
        """
        citas = db.fetch_all(query)
        
        with self.proximas_citas_container:
            self.proximas_citas_container.clear()
            if not citas:
                ui.label('No hay próximas citas programadas').classes('text-gray-400 italic ml-4')
                return
            
            for cita in citas:
                inicial = cita[1][0].upper() if cita[1] else '?'
                hora = cita[3].strftime('%H:%M')
                self.crear_item_lista(inicial, cita[2] or "Procedimiento", hora)

    def load_citas_atencion(self):
        query = """
        SELECT c.id, p.nombre, u.nombre as doctor, c.procedimiento
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        LEFT JOIN usuarios u ON c.doctor_id = u.id
        WHERE c.estado = 'en_curso'
        AND DATE(c.fecha_hora) = CURRENT_DATE
        ORDER BY c.fecha_hora
        """
        citas = db.fetch_all(query)
        
        with self.citas_atencion_container:
            self.citas_atencion_container.clear()
            if not citas:
                ui.label('No hay pacientes siendo atendidos actualmente').classes('text-gray-400 italic ml-4')
                return
            
            for cita in citas:
                inicial = cita[1][0].upper() if cita[1] else '?'
                self.crear_item_lista(inicial, cita[3] or "Procedimiento", cita[2] or "Sin asignar")

    def refresh(self):
        self.load_proximas_citas()
        self.load_citas_atencion()