from nicegui import ui
import database as db
from components.odontograma_view import OdontogramaView

class OdontogramaPage:
    def __init__(self):
        self.paciente_id = None
        self.create_content()
    
    def create_content(self):
        ui.label('Odontograma - Estado Dental').classes('text-h4 mb-4')
        
        # Selector de paciente
        with ui.row().classes('w-full items-center mb-4'):
            self.select_paciente = ui.select(
                label='Seleccionar paciente',
                options={},
                on_change=self.cargar_odontograma
            ).props('outlined').classes('w-96')
            self.cargar_pacientes_select()
        
        # Contenedor principal
        self.contenedor = ui.column().classes('w-full')
        
        # Inicialmente vacío
        self.mostrar_vacio()
    
    def cargar_pacientes_select(self):
        query = "SELECT id, nombre || ' ' || apellidos as nombre FROM pacientes ORDER BY nombre"
        pacientes = db.fetch_all(query)
        options = {None: 'Seleccione un paciente'}
        for p in pacientes:
            options[p[0]] = p[1]
        self.select_paciente.options = options
    
    def mostrar_vacio(self):
        self.contenedor.clear()
        with self.contenedor:
            ui.label('Seleccione un paciente para ver su odontograma').classes('text-italic')
    
    def cargar_odontograma(self):
        self.paciente_id = self.select_paciente.value
        
        if not self.paciente_id:
            self.mostrar_vacio()
            return
        
        self.contenedor.clear()
        
        with self.contenedor:
            # Obtener información del paciente
            query = "SELECT nombre, apellidos FROM pacientes WHERE id = %s"
            paciente_data = db.fetch_one(query, (self.paciente_id,))
            
            if paciente_data:
                ui.label(f"Odontograma de: {paciente_data[0]} {paciente_data[1]}").classes('text-h5 mb-2')
            
            # Crear el odontograma
            odontograma = OdontogramaView(self.paciente_id)
            
            # Tabla de estados dentales
            with ui.expansion('Detalle de Estados Dentales', icon='list').classes('w-full mt-4'):
                self.cargar_tabla_estados()
            
            # Formulario para actualizar estado dental
            with ui.card().classes('w-full mt-4'):
                ui.label('Actualizar Estado Dental').classes('text-h6 mb-2')
                
                with ui.row().classes('w-full items-center'):
                    self.select_diente = ui.select(
                        label='Diente',
                        options=self.generar_opciones_dientes(),
                        value=None
                    ).props('outlined').classes('w-32')
                    
                    self.select_estado = ui.select(
                        label='Estado',
                        options=[
                            ('sano', 'Sano'),
                            ('cariado', 'Cariado'),
                            ('obturado', 'Obturado'),
                            ('extraido', 'Extraído'),
                            ('en_tratamiento', 'En Tratamiento'),
                            ('corona', 'Corona'),
                            ('implante', 'Implante')
                        ],
                        value='sano'
                    ).props('outlined').classes('w-40')
                    
                    self.input_notas = ui.input('Notas').props('outlined').classes('w-64')
                    
                    ui.button('Guardar', on_click=self.guardar_estado, icon='save').props('flat color=primary')
    
    def generar_opciones_dientes(self):
        opciones = {}
        for i in range(1, 33):
            opciones[i] = f"Diente {i}"
        return opciones
    
    def cargar_tabla_estados(self):
        query = """
        SELECT diente_numero, estado, notas, ultima_actualizacion
        FROM estados_dentales
        WHERE paciente_id = %s
        ORDER BY diente_numero
        """
        
        estados = db.fetch_all(query, (self.paciente_id,))
        
        if not estados:
            ui.label('No hay estados dentales registrados').classes('text-italic')
            return
        
        columns = [
            {'name': 'diente', 'label': 'Diente', 'field': 'diente'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'},
            {'name': 'notas', 'label': 'Notas', 'field': 'notas'},
            {'name': 'ultima_actualizacion', 'label': 'Última Actualización', 'field': 'ultima_actualizacion'}
        ]
        
        rows = []
        for estado in estados:
            estado_color = {
                'sano': 'green',
                'cariado': 'red',
                'obturado': 'blue',
                'extraido': 'grey',
                'en_tratamiento': 'orange',
                'corona': 'purple',
                'implante': 'teal'
            }.get(estado[1], 'black')
            
            rows.append({
                'diente': f"Diente {estado[0]}",
                'estado': f"<span style='color: {estado_color}'>{estado[1].title()}</span>",
                'notas': estado[2] or '',
                'ultima_actualizacion': estado[3].strftime('%d/%m/%Y %H:%M')
            })
        
        ui.table(columns=columns, rows=rows, row_key='diente').classes('w-full')
    
    def guardar_estado(self):
        diente = self.select_diente.value
        estado = self.select_estado.value
        notas = self.input_notas.value
        
        if not diente:
            ui.notify('Seleccione un diente', type='warning')
            return
        
        query = """
        INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (paciente_id, diente_numero) 
        DO UPDATE SET estado = EXCLUDED.estado, 
                      notas = EXCLUDED.notas,
                      ultima_actualizacion = CURRENT_TIMESTAMP
        """
        
        try:
            db.execute_query(query, (self.paciente_id, diente, estado, notas))
            ui.notify('Estado dental guardado', type='positive')
            
            # Actualizar la vista
            self.cargar_odontograma()
            
            # Limpiar formulario
            self.input_notas.value = ""
            
        except Exception as e:
            ui.notify(f'Error al guardar: {str(e)}', type='negative')