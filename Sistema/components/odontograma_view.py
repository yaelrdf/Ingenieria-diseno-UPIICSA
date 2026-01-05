from nicegui import ui
import database as db

class OdontogramaView:
    def __init__(self, paciente_id, on_update=None):
        self.paciente_id = paciente_id
        self.on_update = on_update
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
        
        # Valores por defecto para el formulario
        estado_actual = resultado[0] if resultado else 'sano'
        notas_actuales = resultado[1] if resultado else ''
        fecha_actual = resultado[2] if resultado else None
        
        dialog = ui.dialog()
        with dialog:
            with ui.card().classes('min-w-[350px]'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label(f"Diente {numero_diente}").classes('text-h6')
                    ui.badge(nombre, color='primary')
                
                ui.separator().classes('my-2')
                
                if fecha_actual:
                    ui.label(f"Última actualización: {fecha_actual.strftime('%d/%m/%Y %H:%M')}").classes('text-caption text-grey mb-2')
                
                # Formulario de actualización
                ui.label('Actualizar Estado').classes('font-bold mb-1')
                
                select_estado = ui.select(
                    options={
                        'sano': 'Sano',
                        'cariado': 'Cariado',
                        'obturado': 'Obturado',
                        'extraido': 'Extraído',
                        'en_tratamiento': 'En Tratamiento',
                        'corona': 'Corona',
                        'implante': 'Implante'
                    },
                    value=estado_actual
                ).props('outlined dense').classes('w-full mb-2')
                
                input_notas = ui.textarea('Notas', value=notas_actuales).props('outlined dense').classes('w-full mb-4')
                
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancelar', on_click=dialog.close).props('flat color=grey')
                    ui.button('Actualizar', on_click=lambda: self.guardar_estado(numero_diente, select_estado.value, input_notas.value, dialog)).props('color=primary')
        
        dialog.open()

    def guardar_estado(self, diente_numero, estado, notas, dialog):
        query = """
        INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (paciente_id, diente_numero) 
        DO UPDATE SET estado = EXCLUDED.estado, 
                      notas = EXCLUDED.notas,
                      ultima_actualizacion = CURRENT_TIMESTAMP
        """
        
        try:
            db.execute_query(query, (self.paciente_id, diente_numero, estado, notas))
            ui.notify('Estado dental actualizado', type='positive')
            dialog.close()
            if self.on_update:
                self.on_update()
        except Exception as e:
            ui.notify(f'Error al guardar: {str(e)}', type='negative')