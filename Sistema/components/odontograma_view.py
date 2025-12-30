from nicegui import ui
import database as db

class OdontogramaView:
    def __init__(self, paciente_id):
        self.paciente_id = paciente_id
        self.estados_dentales = {}
        self.nombres_dientes = {
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
        self.cargar_estados()
        self.crear_odontograma()
    
    def cargar_estados(self):
        query = "SELECT diente_numero, estado FROM estados_dentales WHERE paciente_id = %s"
        resultados = db.fetch_all(query, (self.paciente_id,))
        self.estados_dentales = {r[0]: r[1] for r in resultados}
    
    def crear_odontograma(self):
        # Mapa de colores para los estados
        colores_estado = {
            'sano': '#4CAF50',  # Verde (Healthy)
            'cariado': '#F44336',  # Rojo (Caries)
            'obturado': '#2196F3',  # Azul (Restored)
            'extraido': '#000000',  # Negro (Missing)
            'en_tratamiento': '#FF9800',  # Naranja
            'corona': '#9C27B0',  # Púrpura
            'implante': '#00BCD4'  # Turquesa
        }
        
        with ui.card().classes('w-full p-4 overflow-auto'):
            # Maxilar Superior
            ui.label('Maxilar Superior').classes('text-center font-bold mb-2 w-full')
            with ui.row().classes('w-full justify-center gap-1 mb-8 no-wrap'):
                # Cuadrante Superior Derecho (8 a 1)
                for diente in range(1, 9):
                    self.crear_diente_vista(diente, colores_estado)
                
                ui.element('div').classes('w-4') # Espacio central
                
                # Cuadrante Superior Izquierdo (9 a 16)
                for diente in range(9, 17):
                    self.crear_diente_vista(diente, colores_estado)
            
            ui.separator().classes('my-4')
            
            # Mandíbula Inferior
            ui.label('Mandíbula Inferior').classes('text-center font-bold mb-2 w-full')
            with ui.row().classes('w-full justify-center gap-1 no-wrap'):
                # Cuadrante Inferior Derecho (32 a 25)
                for diente in range(32, 24, -1):
                    self.crear_diente_vista(diente, colores_estado)
                
                ui.element('div').classes('w-4') # Espacio central
                
                # Cuadrante Inferior Izquierdo (24 a 17)
                for diente in range(24, 16, -1):
                    self.crear_diente_vista(diente, colores_estado)
    
    def crear_diente_vista(self, numero_diente, colores_estado):
        estado = self.estados_dentales.get(numero_diente, 'sano')
        color = colores_estado.get(estado, '#4CAF50')
        nombre = self.nombres_dientes.get(numero_diente, f"Diente {numero_diente}")
        
        with ui.column().classes('items-center width-12'):
            # Círculo representando el diente
            diente_el = ui.element('div').style(f'''
                width: 35px;
                height: 35px;
                background-color: {color};
                border-radius: 4px;
                border: 2px solid #333;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: transform 0.2s;
            ''').on('click', lambda n=numero_diente: self.mostrar_detalle_diente(n))
            
            with diente_el:
                ui.label(str(numero_diente)).classes('text-white font-bold text-xs')
            
            ui.tooltip(nombre)
            
            # Estado abreviado
            estado_abrev = {
                'sano': 'S',
                'cariado': 'C',
                'obturado': 'O',
                'extraido': 'X',
                'en_tratamiento': 'T',
                'corona': 'CR',
                'implante': 'I'
            }.get(estado, estado[:1].upper())
            
            ui.label(estado_abrev).classes('text-[10px] font-bold mt-1')
    
    def mostrar_detalle_diente(self, numero_diente):
        query = """
        SELECT estado, notas, ultima_actualizacion
        FROM estados_dentales
        WHERE paciente_id = %s AND diente_numero = %s
        """
        
        resultado = db.fetch_one(query, (self.paciente_id, numero_diente))
        nombre = self.nombres_dientes.get(numero_diente, f"Diente {numero_diente}")
        
        dialog = ui.dialog()
        with dialog:
            with ui.card().classes('min-w-[300px]'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label(f"Diente {numero_diente}").classes('text-h6')
                    ui.badge(nombre, color='primary')
                
                ui.separator().classes('my-2')
                
                if resultado:
                    estado = resultado[0]
                    notas = resultado[1]
                    fecha = resultado[2]
                    
                    ui.label(f"Estado: {estado.title()}").classes('text-subtitle1')
                    ui.label(f"Última actualización: {fecha.strftime('%d/%m/%Y %H:%M')}").classes('text-caption text-grey')
                    
                    if notas:
                        ui.separator().classes('my-2')
                        ui.label('Notas:').classes('font-bold')
                        ui.markdown(notas).classes('text-body2 bg-grey-1 p-2 rounded')
                else:
                    ui.label('No hay información registrada para este diente').classes('text-italic text-grey')
                
                with ui.row().classes('w-full justify-end mt-4'):
                    ui.button('Cerrar', on_click=dialog.close).props('flat')
        
        dialog.open()