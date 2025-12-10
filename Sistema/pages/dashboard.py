from nicegui import ui
from datetime import datetime, timedelta
import database as db

class DashboardPage:
    def __init__(self):
        self.create_content()
    
    def create_content(self):
        ui.label('Dashboard').classes('text-h4 mb-4')
        
        with ui.row().classes('w-full'):
            with ui.card().classes('w-1/2'):
                ui.label('Citas en Atención').classes('text-h6')
                self.citas_atencion = ui.column()
                self.load_citas_atencion()
            
            with ui.card().classes('w-1/2'):
                ui.label('Próximas Citas').classes('text-h6')
                self.proximas_citas = ui.column()
                self.load_proximas_citas()
        
        with ui.card().classes('w-full mt-4'):
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Resumen del Día').classes('text-h6')
                ui.button('Actualizar', icon='refresh', on_click=self.refresh)
            
            with ui.row().classes('w-full'):
                with ui.card().classes('w-1/4'):
                    ui.label('Citas Hoy').classes('text-center')
                    self.citas_hoy = ui.label('0').classes('text-h4 text-center text-primary')
                
                with ui.card().classes('w-1/4'):
                    ui.label('Pacientes Nuevos').classes('text-center')
                    self.pacientes_nuevos = ui.label('0').classes('text-h4 text-center text-green')
                
                with ui.card().classes('w-1/4'):
                    ui.label('Procedimientos Pendientes').classes('text-center')
                    self.procedimientos_pendientes = ui.label('0').classes('text-h4 text-center text-orange')
                
                with ui.card().classes('w-1/4'):
                    ui.label('Adeudos Totales').classes('text-center')
                    self.adeudos_totales = ui.label('$0.00').classes('text-h4 text-center text-red')
            
            self.load_resumen()
    
    def load_citas_atencion(self):
        query = """
        SELECT c.id, p.nombre || ' ' || p.apellidos as paciente, 
               u.nombre as doctor, c.procedimiento, c.fecha_hora
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        LEFT JOIN usuarios u ON c.doctor_id = u.id
        WHERE c.estado = 'en_curso'
        AND DATE(c.fecha_hora) = CURRENT_DATE
        ORDER BY c.fecha_hora
        """
        
        citas = db.fetch_all(query)
        
        with self.citas_atencion:
            self.citas_atencion.clear()
            
            if not citas:
                ui.label('No hay citas en atención').classes('text-italic')
                return
            
            for cita in citas:
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full justify-between'):
                        ui.label(f"Paciente: {cita[1]}").classes('font-bold')
                        ui.label(f"Hora: {cita[4].strftime('%H:%M')}")
                    ui.label(f"Doctor: {cita[2] or 'Sin asignar'}")
                    ui.label(f"Procedimiento: {cita[3]}")
    
    def load_proximas_citas(self):
        query = """
        SELECT c.id, p.nombre || ' ' || p.apellidos as paciente, 
               c.procedimiento, c.fecha_hora
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        WHERE c.estado = 'programada'
        AND c.fecha_hora > CURRENT_TIMESTAMP
        ORDER BY c.fecha_hora
        LIMIT 5
        """
        
        citas = db.fetch_all(query)
        
        with self.proximas_citas:
            self.proximas_citas.clear()
            
            if not citas:
                ui.label('No hay próximas citas').classes('text-italic')
                return
            
            for cita in citas:
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full justify-between'):
                        ui.label(f"Paciente: {cita[1]}").classes('font-bold')
                        ui.label(f"Hora: {cita[3].strftime('%H:%M')}")
                    ui.label(f"Procedimiento: {cita[2]}")
    
    def load_resumen(self):
        # Citas hoy
        query = "SELECT COUNT(*) FROM citas WHERE DATE(fecha_hora) = CURRENT_DATE"
        citas_hoy = db.fetch_one(query)
        self.citas_hoy.set_text(str(citas_hoy[0] if citas_hoy else 0))
        
        # Pacientes nuevos (últimos 7 días)
        query = "SELECT COUNT(*) FROM pacientes WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
        pacientes_nuevos = db.fetch_one(query)
        self.pacientes_nuevos.set_text(str(pacientes_nuevos[0] if pacientes_nuevos else 0))
        
        # Procedimientos pendientes
        query = "SELECT COUNT(*) FROM procedimientos_paciente WHERE estado = 'pendiente'"
        procedimientos_pend = db.fetch_one(query)
        self.procedimientos_pendientes.set_text(str(procedimientos_pend[0] if procedimientos_pend else 0))
        
        # Adeudos totales
        query = """
        SELECT COALESCE(SUM(pp.costo), 0) - COALESCE(SUM(pg.monto), 0) as adeudo
        FROM procedimientos_paciente pp
        LEFT JOIN pagos pg ON pp.id = pg.procedimiento_id
        WHERE pp.estado = 'completado'
        """
        adeudos = db.fetch_one(query)
        total = adeudos[0] if adeudos else 0
        self.adeudos_totales.set_text(f"${total:,.2f}")
    
    def refresh(self):
        self.load_citas_atencion()
        self.load_proximas_citas()
        self.load_resumen()