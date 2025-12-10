from nicegui import ui
import database as db

class OdontogramaView:
    def __init__(self, paciente_id):
        self.paciente_id = paciente_id
        self.estados_dentales = {}
        self.cargar_estados()
        self.crear_odontograma()
    
    def cargar_estados(self):
        query = "SELECT diente_numero, estado FROM estados_dentales WHERE paciente_id = %s"
        resultados = db.fetch_all(query, (self.paciente_id,))
        self.estados_dentales = {r[0]: r[1] for r in resultados}
    
    def crear_odontograma(self):
        # Mapa de colores para los estados
        colores_estado = {
            'sano': '#4CAF50',  # Verde
            'cariado': '#F44336',  # Rojo
            'obturado': '#2196F3',  # Azul
            'extraido': '#9E9E9E',  # Gris
            'en_tratamiento': '#FF9800',  # Naranja
            'corona': '#9C27B0',  # Púrpura
            'implante': '#00BCD4'  # Turquesa
        }
        
        # Odontograma simplificado - vista superior
        with ui.card().classes('w-full p-4'):
            ui.label('Vista Superior (Maxilar)').classes('text-center font-bold mb-2')
            
            # Dientes superiores (16-11, 21-26)
            with ui.row().classes('w-full justify-center gap-1 mb-4'):
                for diente in range(16, 10, -1):
                    if diente == 11:
                        continue  # Saltar el espacio central
                    self.crear_diente_vista(diente, colores_estado)
            
            # Línea divisoria
            ui.separator().classes('my-4')
            
            ui.label('Vista Inferior (Mandibular)').classes('text-center font-bold mb-2')
            
            # Dientes inferiores (46-41, 31-36)
            with ui.row().classes('w-full justify-center gap-1'):
                for diente in range(46, 40, -1):
                    if diente == 41:
                        continue  # Saltar el espacio central
                    self.crear_diente_vista(diente, colores_estado)
    
    def crear_diente_vista(self, numero_diente, colores_estado):
        estado = self.estados_dentales.get(numero_diente, 'sano')
        color = colores_estado.get(estado, '#4CAF50')
        
        with ui.column().classes('items-center'):
            # Círculo representando el diente
            ui.element('div').style(f'''
                width: 40px;
                height: 40px;
                background-color: {color};
                border-radius: 50%;
                border: 2px solid #333;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                margin-bottom: 4px;
            ''').on('click', lambda n=numero_diente: self.mostrar_detalle_diente(n))
            
            # Número del diente
            ui.label(str(numero_diente)).classes('text-xs font-bold')
            
            # Estado abreviado
            estado_abrev = {
                'sano': 'S',
                'cariado': 'C',
                'obturado': 'O',
                'extraido': 'E',
                'en_tratamiento': 'T',
                'corona': 'CR',
                'implante': 'I'
            }.get(estado, estado[:2].upper())
            
            ui.label(estado_abrev).classes('text-xs')
    
    def mostrar_detalle_diente(self, numero_diente):
        query = """
        SELECT estado, notas, ultima_actualizacion
        FROM estados_dentales
        WHERE paciente_id = %s AND diente_numero = %s
        """
        
        resultado = db.fetch_one(query, (self.paciente_id, numero_diente))
        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label(f"Diente {numero_diente}").classes('text-h6 mb-2')
                
                if resultado:
                    estado = resultado[0]
                    notas = resultado[1]
                    fecha = resultado[2]
                    
                    ui.label(f"Estado: {estado.title()}")
                    ui.label(f"Última actualización: {fecha.strftime('%d/%m/%Y %H:%M')}")
                    
                    if notas:
                        ui.separator()
                        ui.label('Notas:').classes('font-bold')
                        ui.markdown(notas).classes('text-body2')
                else:
                    ui.label('No hay información registrada para este diente').classes('text-italic')
                
                with ui.row().classes('justify-end mt-4'):
                    ui.button('Cerrar', on_click=dialog.close)
        
        dialog.open()