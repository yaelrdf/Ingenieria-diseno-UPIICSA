from nicegui import ui

import database as db
import validaciones as val
from components.confirmacion import confirmar
from components.paciente_form import PacienteForm
from models.paciente import Paciente
from pages.citas import puede_eliminar_usuario


class PacientesPage:
    def __init__(self):
        self.puede_eliminar = puede_eliminar_usuario()
        self.pacientes_container = None
        self.create_content()

    def create_content(self):
        ui.label('Gestión de Pacientes').classes('text-h4 mb-4')

        with ui.row().classes('w-full items-center mb-4'):
            self.search_input = ui.input('Buscar paciente', on_change=self.buscar_pacientes,
                                         placeholder='Nombre, CURP o teléfono').props('outlined clearable').classes('w-96')
            ui.button('Nuevo Paciente', on_click=self.mostrar_form_nuevo, icon='person_add').props('flat color=primary')

        self.pacientes_container = ui.column().classes('w-full gap-3')
        self.cargar_pacientes()

    def cargar_pacientes(self, query=None):
        query = val.texto(query)
        if query:
            search = f'%{query}%'
            resultados = db.fetch_all("""
                SELECT id, nombre || ' ' || apellidos, curp, telefono, email
                FROM pacientes
                WHERE nombre ILIKE %s OR apellidos ILIKE %s OR (nombre || ' ' || apellidos) ILIKE %s
                   OR curp ILIKE %s OR telefono ILIKE %s
                ORDER BY nombre, apellidos
            """, (search, search, search, search, search))
        else:
            resultados = db.fetch_all("""
                SELECT id, nombre || ' ' || apellidos, curp, telefono, email
                FROM pacientes ORDER BY nombre, apellidos
            """)

        self.pacientes_container.clear()
        with self.pacientes_container:
            if not resultados:
                ui.label('No se encontraron resultados' if query else 'No hay pacientes registrados') \
                    .classes('text-subtitle2 italic text-gray-500')
                return
            for paciente in resultados:
                self.crear_tarjeta_paciente(*paciente)

    def crear_tarjeta_paciente(self, paciente_id, nombre, curp, telefono, email):
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-start'):
                with ui.column().classes('flex-grow'):
                    ui.label(nombre).classes('text-h6 font-bold')
                    with ui.row().classes('gap-8'):
                        with ui.column().classes('gap-1'):
                            ui.label('CURP').classes('text-caption text-gray-600')
                            ui.label(curp).classes('text-body2 font-mono')
                        with ui.column().classes('gap-1'):
                            ui.label('Teléfono').classes('text-caption text-gray-600')
                            ui.label(val.mostrar(telefono)).classes('text-body2')
                        with ui.column().classes('gap-1'):
                            ui.label('Email').classes('text-caption text-gray-600')
                            ui.label(val.mostrar(email)).classes('text-body2 break-all')

                with ui.column().classes('items-end gap-2'):
                    with ui.row().classes('gap-2'):
                        ui.button(icon='edit', on_click=lambda id=paciente_id: self.editar_paciente(id)).props('flat').tooltip('Editar')
                        ui.button(icon='visibility', on_click=lambda id=paciente_id: self.ver_expediente(id)).props('flat color=blue').tooltip('Ver expediente')
                    if self.puede_eliminar:
                        ui.button(icon='delete', on_click=lambda id=paciente_id, n=nombre: self.eliminar_paciente(id, n)) \
                            .props('flat color=red').tooltip('Eliminar')

    def buscar_pacientes(self):
        self.cargar_pacientes(self.search_input.value)

    def mostrar_form_nuevo(self):
        def guardar_paciente(paciente):
            try:
                db.execute_query("""
                    INSERT INTO pacientes (curp, nombre, apellidos, fecha_nacimiento, edad, genero,
                                           telefono, email, direccion, alergias, enfermedades_cronicas,
                                           medicamentos, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (paciente.curp, paciente.nombre, paciente.apellidos, paciente.fecha_nacimiento,
                      paciente.edad, paciente.genero, paciente.telefono, paciente.email,
                      paciente.direccion, paciente.alergias, paciente.enfermedades_cronicas,
                      paciente.medicamentos, paciente.observaciones))
                ui.notify('Paciente guardado exitosamente', type='positive')
                self.cargar_pacientes(self.search_input.value)
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al guardar: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog() as dialog:
            PacienteForm(on_save=guardar_paciente, on_cancel=dialog.close)
        dialog.open()

    def editar_paciente(self, paciente_id):
        fila = db.fetch_one("""
            SELECT id, curp, nombre, apellidos, fecha_nacimiento, edad, genero, telefono, email, direccion,
                   alergias, enfermedades_cronicas, medicamentos, observaciones
            FROM pacientes WHERE id = %s
        """, (paciente_id,))
        if not fila:
            ui.notify('Paciente no encontrado', type='warning')
            return

        paciente = Paciente(
            id=fila[0], curp=fila[1], nombre=fila[2], apellidos=fila[3], fecha_nacimiento=fila[4],
            edad=fila[5], genero=fila[6], telefono=fila[7], email=fila[8], direccion=fila[9],
            alergias=fila[10], enfermedades_cronicas=fila[11], medicamentos=fila[12], observaciones=fila[13]
        )

        def actualizar_paciente(p):
            try:
                db.execute_query("""
                    UPDATE pacientes SET
                        curp=%s, nombre=%s, apellidos=%s, fecha_nacimiento=%s,
                        edad=%s, genero=%s, telefono=%s, email=%s, direccion=%s,
                        alergias=%s, enfermedades_cronicas=%s, medicamentos=%s, observaciones=%s,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=%s
                """, (p.curp, p.nombre, p.apellidos, p.fecha_nacimiento, p.edad, p.genero, p.telefono,
                      p.email, p.direccion, p.alergias, p.enfermedades_cronicas, p.medicamentos,
                      p.observaciones, p.id))
                ui.notify('Paciente actualizado exitosamente', type='positive')
                self.cargar_pacientes(self.search_input.value)
                dialog.close()
            except Exception as e:
                ui.notify(f'Error al actualizar: {val.mensaje_error_bd(e)}', type='negative')

        with ui.dialog() as dialog:
            PacienteForm(paciente=paciente, on_save=actualizar_paciente, on_cancel=dialog.close)
        dialog.open()

    def eliminar_paciente(self, paciente_id, nombre):
        def eliminar():
            try:
                db.execute_query('DELETE FROM pacientes WHERE id = %s', (paciente_id,))
                ui.notify('Paciente eliminado', type='positive')
                self.cargar_pacientes(self.search_input.value)
            except Exception as e:
                ui.notify(f'Error al eliminar: {val.mensaje_error_bd(e)}', type='negative')

        confirmar('¿Eliminar paciente?',
                  f'Se eliminará a {nombre} junto con sus citas, pagos y expediente. Esta acción no se puede deshacer.',
                  eliminar, texto_confirmar='Eliminar', color='red')

    def ver_expediente(self, paciente_id):
        ui.navigate.to(f'/expedientes?paciente_id={paciente_id}')
