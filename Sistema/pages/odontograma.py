from nicegui import ui
import database as db
from components.odontograma_view import OdontogramaView
from components.paciente_selector import PacienteSelector

class OdontogramaPage:
    nombres_dientes = {
        1: "3er Molar Superior Derecho", 2: "2do Molar Superior Derecho", 3: "1er Molar Superior Derecho",
        4: "2do Premolar Superior Derecho", 5: "1er Premolar Superior Derecho", 6: "Canino Superior Derecho",
        7: "Incisivo Lateral Superior Derecho", 8: "Incisivo Central Superior Derecho",
        9: "Incisivo Central Superior Izquierdo", 10: "Incisivo Lateral Superior Izquierdo",
        11: "Canino Superior Izquierdo", 12: "1er Premolar Superior Izquierdo",
        13: "2do Premolar Superior Izquierdo", 14: "1er Molar Superior Izquierdo",
        15: "2do Molar Superior Izquierdo", 16: "3er Molar Superior Izquierdo",
        17: "3er Molar Inferior Izquierdo", 18: "2do Molar Inferior Izquierdo", 19: "1er Molar Inferior Izquierdo",
        20: "2do Premolar Inferior Izquierdo", 21: "1er Premolar Inferior Izquierdo",
        22: "Canino Inferior Izquierdo", 23: "Incisivo Lateral Inferior Izquierdo", 24: "Incisivo Central Inferior Izquierdo",
        25: "Incisivo Central Inferior Derecho", 26: "Incisivo Lateral Inferior Derecho",
        27: "Canino Inferior Derecho", 28: "1er Premolar Inferior Derecho",
        29: "2do Premolar Inferior Derecho", 30: "1er Molar Inferior Derecho",
        31: "2do Molar Inferior Derecho", 32: "3er Molar Inferior Derecho"
    }

    def __init__(self):
        self.paciente_id = None
        self.create_content()
    
    def create_content(self):
        ui.label('Odontograma - Estado Dental').classes('text-h4 mb-4')
        
        # Selector de paciente
        with ui.row().classes('w-full items-center mb-4 gap-4'):
            ui.button('Seleccionar Paciente', icon='person_search', on_click=self.abrir_selector).props('outline color=primary')
            
            self.paciente_display = ui.row().classes('items-center gap-2 bg-blue-50 p-2 rounded')
            with self.paciente_display:
                ui.icon('person', color='primary')
                self.label_paciente = ui.label('Seleccione un paciente').classes('font-bold')
            
            self.paciente_display.set_visibility(self.paciente_id is not None)
        
        # Contenedor principal
        self.contenedor = ui.column().classes('w-full')
        
        # Inicialmente vacío
        self.mostrar_vacio()
    
    def abrir_selector(self):
        PacienteSelector(on_select=self.seleccionar_paciente).open()
        
    def seleccionar_paciente(self, pid, name):
        self.paciente_id = pid
        self.label_paciente.set_text(name)
        self.paciente_display.set_visibility(True)
        self.cargar_odontograma()

    def mostrar_vacio(self):
        self.contenedor.clear()
        with self.contenedor:
            ui.label('Seleccione un paciente para ver su odontograma').classes('text-italic')
    
    def cargar_odontograma(self):
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
                        options={
                            'sano': 'Sano',
                            'cariado': 'Cariado',
                            'obturado': 'Obturado',
                            'extraido': 'Extraído',
                            'en_tratamiento': 'En Tratamiento',
                            'corona': 'Corona',
                            'implante': 'Implante'
                        },
                        value='sano'
                    ).props('outlined').classes('w-40')
                    
                    self.input_notas = ui.input('Notas').props('outlined').classes('w-64')
                    
                    ui.button('Guardar', on_click=self.guardar_estado, icon='save').props('flat color=primary')
    
    def generar_opciones_dientes(self):
        opciones = {}
        for i in range(1, 33):
            opciones[i] = f"{i} - {self.nombres_dientes.get(i, f'Diente {i}')}"
        return opciones
    
    def cargar_tabla_estados(self):
        query = """
        SELECT diente_numero, estado, notas, ultima_actualizacion
        FROM estados_dentales
        WHERE paciente_id = %s
        ORDER BY diente_numero
        """
        
        estados = db.fetch_all(query, (self.paciente_id,))
        
        columns = [
            {'name': 'diente', 'label': 'Diente', 'field': 'diente'},
            {'name': 'estado', 'label': 'Estado', 'field': 'estado'},
            {'name': 'estado_color', 'label': 'Color', 'field': 'estado_color'}, # Oculto por defecto? No, field no está en columns
            {'name': 'notas', 'label': 'Notas', 'field': 'notas'},
            {'name': 'ultima_actualizacion', 'label': 'Última Actualización', 'field': 'ultima_actualizacion'}
        ]
        
        rows = []
        for estado in estados:
            estado_color = {
                'sano': 'green',
                'cariado': 'red',
                'obturado': 'blue',
                'extraido': 'black',
                'en_tratamiento': 'orange',
                'corona': 'purple',
                'implante': 'teal'
            }.get(estado[1], 'grey')
            
            rows.append({
                'diente': f"{estado[0]} - {self.nombres_dientes.get(estado[0], '')}",
                'estado': estado[1],
                'estado_color': estado_color,
                'notas': estado[2] or '',
                'ultima_actualizacion': estado[3].strftime('%d/%m/%Y %H:%M')
            })
        
        table = ui.table(columns=columns, rows=rows, row_key='diente').classes('w-full')
        table.add_slot('body-cell-estado', '''
            <q-td :props="props">
                <q-badge :color="props.row.estado_color">
                    {{ props.value }}
                </q-badge>
            </q-td>
        ''')
    
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