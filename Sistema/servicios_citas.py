"""Operaciones de citas compartidas por "Vista general" y "Gestión de citas"."""
from datetime import datetime
from typing import Optional

import database as db
import validaciones as val
from models.cita import Cita

TIPOS_CITA = {
    'consulta': 'Consulta',
    'limpieza': 'Limpieza Dental',
    'procedimiento': 'Procedimiento',
    'revision': 'Revisión',
    'urgencia': 'Urgencia',
}

ESTADOS_CITA = {
    'programada': 'Programada',
    'en_curso': 'En Curso',
    'completada': 'Completada',
    'cancelada': 'Cancelada',
}

COLORES_ESTADO = {
    'programada': 'blue',
    'en_curso': 'orange',
    'completada': 'green',
    'cancelada': 'red',
}

# Estado de origen permitido para cada cambio de estado rápido
TRANSICIONES = {
    'en_curso': ('programada',),
    'completada': ('programada', 'en_curso'),
    'cancelada': ('programada', 'en_curso'),
}


def _al_minuto(valor: Optional[datetime]) -> Optional[datetime]:
    return valor.replace(second=0, microsecond=0) if valor else None


def validar_cita(cita: Cita, original: Optional[Cita] = None) -> Optional[str]:
    """Reglas de negocio de una cita nueva o editada. Devuelve el mensaje de error o None."""
    if not cita.paciente_id:
        return 'Seleccione un paciente'
    if not cita.tipo:
        return 'El tipo de cita es obligatorio'
    if not cita.fecha_hora:
        return 'Seleccione fecha y hora válidas'
    if (cita.costo or 0) < 0:
        return 'El costo no puede ser negativo'

    activa = cita.estado in val.ESTADOS_CITA_ACTIVOS
    ahora = _al_minuto(datetime.now())
    cambio_fecha = original is None or _al_minuto(original.fecha_hora) != _al_minuto(cita.fecha_hora)
    if activa and cambio_fecha and cita.fecha_hora < ahora:
        return 'La fecha y hora de la cita no puede estar en el pasado'

    if cita.doctor_id and activa:
        if not val.medico_activo(cita.doctor_id):
            return 'El médico seleccionado está inactivo y no puede asignarse a citas (RN05)'
        empalme = val.buscar_empalme(cita.doctor_id, cita.fecha_hora, cita.duracion_minutos, cita.id)
        if empalme:
            return (f'El médico ya tiene una cita el {empalme[1]} con {empalme[2]} '
                    'que se traslapa con este horario')
    return None


def _sincronizar_procedimiento(cursor, cita_id):
    """Al completar una cita con costo se registra (o actualiza) el adeudo del paciente."""
    cursor.execute('SELECT paciente_id, costo, tipo, procedimiento, fecha_hora FROM citas WHERE id = %s', (cita_id,))
    fila = cursor.fetchone()
    if not fila or float(fila[1] or 0) <= 0:
        return
    paciente_id, costo, tipo, descripcion, fecha_hora = fila
    notas = f'{tipo.upper()}: {descripcion}' if descripcion else tipo.upper()

    cursor.execute('SELECT id FROM procedimientos_paciente WHERE cita_id = %s', (cita_id,))
    if cursor.fetchone():
        cursor.execute("""
            UPDATE procedimientos_paciente
            SET costo = %s, fecha_realizacion = %s, notas = %s, estado = 'completado', paciente_id = %s
            WHERE cita_id = %s
        """, (costo, fecha_hora.date(), notas, paciente_id, cita_id))
    else:
        cursor.execute("""
            INSERT INTO procedimientos_paciente (paciente_id, cita_id, costo, estado, fecha_realizacion, notas)
            VALUES (%s, %s, %s, 'completado', %s, %s)
        """, (paciente_id, cita_id, costo, fecha_hora.date(), notas))


def crear_cita(cita: Cita) -> int:
    """Registra una cita nueva; siempre inicia como 'programada'."""
    with db.transaction() as cursor:
        cursor.execute("""
            INSERT INTO citas (paciente_id, doctor_id, fecha_hora, tipo, procedimiento,
                               estado, notas, duracion_minutos, costo)
            VALUES (%s, %s, %s, %s, %s, 'programada', %s, %s, %s)
            RETURNING id
        """, (cita.paciente_id, cita.doctor_id, cita.fecha_hora, cita.tipo, cita.procedimiento,
              cita.notas, cita.duracion_minutos, cita.costo))
        return cursor.fetchone()[0]


def obtener_cita(cita_id) -> Optional[Cita]:
    fila = db.fetch_one("""
        SELECT id, paciente_id, doctor_id, fecha_hora, tipo, procedimiento, estado,
               notas, duracion_minutos, costo
        FROM citas WHERE id = %s
    """, (cita_id,))
    if not fila:
        return None
    return Cita(id=fila[0], paciente_id=fila[1], doctor_id=fila[2], fecha_hora=fila[3], tipo=fila[4],
                procedimiento=fila[5] or '', estado=fila[6], notas=fila[7] or '',
                duracion_minutos=fila[8], costo=float(fila[9] or 0))


def actualizar_cita(cita: Cita):
    with db.transaction() as cursor:
        cursor.execute("""
            UPDATE citas SET paciente_id = %s, doctor_id = %s, fecha_hora = %s, tipo = %s,
                             procedimiento = %s, estado = %s, notas = %s, duracion_minutos = %s, costo = %s
            WHERE id = %s
        """, (cita.paciente_id, cita.doctor_id, cita.fecha_hora, cita.tipo, cita.procedimiento,
              cita.estado, cita.notas, cita.duracion_minutos, cita.costo, cita.id))
        if cita.estado == 'completada':
            _sincronizar_procedimiento(cursor, cita.id)


def cambiar_estado(cita_id, nuevo_estado: str) -> bool:
    """Cambia el estado si la transición es válida. Devuelve False si la cita ya no lo permite."""
    with db.transaction() as cursor:
        cursor.execute('UPDATE citas SET estado = %s WHERE id = %s AND estado = ANY(%s)',
                       (nuevo_estado, cita_id, list(TRANSICIONES[nuevo_estado])))
        if cursor.rowcount == 0:
            return False
        if nuevo_estado == 'completada':
            _sincronizar_procedimiento(cursor, cita_id)
        return True


def eliminar_cita(cita_id):
    db.execute_query('DELETE FROM citas WHERE id = %s', (cita_id,))
