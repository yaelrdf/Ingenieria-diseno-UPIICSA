"""Reglas de validación compartidas por formularios y páginas."""
import re
from datetime import date, datetime, timedelta
from typing import Optional

import psycopg2
import psycopg2.errors

import database as db

CURP_RE = re.compile(r'^[A-Z0-9]{18}$')
EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$')
TELEFONO_RE = re.compile(r'^\d{10}$')

ESTADOS_CITA_ACTIVOS = ('programada', 'en_curso')


def texto(valor) -> str:
    return (valor or '').strip()


# ---------------------------------------------------------------------------
# Validadores de campo: devuelven el mensaje de error o None si es válido.
# Se usan como `validation=` de NiceGUI (validación en tiempo real) y al guardar.
# ---------------------------------------------------------------------------

def validar_curp(valor) -> Optional[str]:
    curp = texto(valor).upper()
    if not curp:
        return 'El CURP es obligatorio'
    if not re.fullmatch(r'[A-Z0-9]*', curp):
        return 'El CURP solo admite letras y números, sin espacios ni caracteres especiales'
    if len(curp) != 18:
        return f'El CURP debe tener exactamente 18 caracteres (lleva {len(curp)})'
    return None


def validar_obligatorio(nombre_campo: str):
    def validar(valor) -> Optional[str]:
        return None if texto(valor) else f'{nombre_campo} es obligatorio'
    return validar


def validar_email(valor, obligatorio: bool = False) -> Optional[str]:
    email = texto(valor)
    if not email:
        return 'El email es obligatorio' if obligatorio else None
    if not EMAIL_RE.fullmatch(email):
        return 'Formato de email inválido (ejemplo: nombre@dominio.com)'
    return None


def validar_telefono(valor) -> Optional[str]:
    telefono = texto(valor)
    if telefono and not TELEFONO_RE.fullmatch(telefono):
        return 'El teléfono debe tener 10 dígitos numéricos'
    return None


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def calcular_edad(fecha_nacimiento) -> Optional[int]:
    if not fecha_nacimiento:
        return None
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))


def parse_fecha(valor) -> Optional[date]:
    """Convierte el valor de un selector de fecha (str ISO o date) a date. Lanza ValueError si es inválido."""
    if not valor:
        return None
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor).strip().replace('/', '-'))


def mostrar(valor, vacio: str = 'N/A') -> str:
    """Texto para mostrar en pantalla sin 'None'."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return vacio
    return str(valor)


# ---------------------------------------------------------------------------
# Reglas que consultan la base de datos
# ---------------------------------------------------------------------------

def medico_activo(medico_id) -> bool:
    fila = db.fetch_one('SELECT activo FROM usuarios WHERE id = %s', (medico_id,))
    return bool(fila and fila[0])


def contar_citas_medico(medico_id, solo_activas: bool = False) -> int:
    sql = 'SELECT COUNT(*) FROM citas WHERE doctor_id = %s'
    if solo_activas:
        sql += " AND estado IN ('programada', 'en_curso')"
    return db.fetch_one(sql, (medico_id,))[0]


def buscar_empalme(doctor_id, inicio: datetime, duracion_minutos: int, excluir_cita_id=None):
    """Devuelve (id, 'DD/MM/YYYY HH:MI', paciente) de una cita activa del médico que se traslape, o None."""
    fin = inicio + timedelta(minutes=int(duracion_minutos))
    return db.fetch_one(
        """
        SELECT c.id, TO_CHAR(c.fecha_hora, 'DD/MM/YYYY HH24:MI'), p.nombre || ' ' || p.apellidos
        FROM citas c
        JOIN pacientes p ON p.id = c.paciente_id
        WHERE c.doctor_id = %s
          AND c.estado IN ('programada', 'en_curso')
          AND c.id <> %s
          AND c.fecha_hora < %s
          AND c.fecha_hora + make_interval(mins => c.duracion_minutos) > %s
        ORDER BY c.fecha_hora
        LIMIT 1
        """,
        (doctor_id, excluir_cita_id or 0, fin, inicio),
    )


_MENSAJES_RESTRICCION = {
    'pacientes_curp_key': 'Ya existe un paciente registrado con ese CURP',
    'pacientes_curp_formato': 'El CURP debe tener exactamente 18 letras o números',
    'usuarios_email_key': 'Ya existe un médico registrado con ese email',
    'usuarios_email_formato': 'Formato de email inválido',
    'usuarios_sistema_username_key': 'El nombre de usuario ya existe',
    'citas_doctor_id_fkey': 'El médico tiene citas registradas y no puede eliminarse',
}


def mensaje_error_bd(error: Exception) -> str:
    """Traduce errores de PostgreSQL a mensajes comprensibles para el usuario."""
    if isinstance(error, psycopg2.Error):
        restriccion = getattr(getattr(error, 'diag', None), 'constraint_name', None)
        if restriccion in _MENSAJES_RESTRICCION:
            return _MENSAJES_RESTRICCION[restriccion]
        if isinstance(error, psycopg2.errors.UniqueViolation):
            return 'Ya existe un registro con esos datos'
        if isinstance(error, psycopg2.errors.ForeignKeyViolation):
            return 'El registro está relacionado con otros datos y no puede modificarse'
        if isinstance(error, psycopg2.errors.CheckViolation):
            return 'Alguno de los datos no cumple el formato requerido'
        if isinstance(error, psycopg2.OperationalError):
            return 'No fue posible conectar con la base de datos, intente de nuevo'
    return f'Error inesperado: {error}'
