-- =====================================================================
-- Sonrisa Perfecta v1.1.0 - Esquema de base de datos
-- Se ejecuta automáticamente la primera vez que se crea el volumen de
-- PostgreSQL (docker-entrypoint-initdb.d), sobre la base POSTGRES_DB.
-- =====================================================================

-- Médicos / dentistas
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
        CONSTRAINT usuarios_email_formato
        CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9-]+(\.[A-Z0-9-]+)*\.[A-Z]{2,}$'),
    telefono VARCHAR(20),
    especialidad VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pacientes
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    curp VARCHAR(18) UNIQUE NOT NULL
        CONSTRAINT pacientes_curp_formato CHECK (curp ~ '^[A-Z0-9]{18}$'),
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    edad INTEGER,  -- Obsoleto: la edad se calcula a partir de fecha_nacimiento
    genero VARCHAR(10),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    alergias TEXT,
    enfermedades_cronicas TEXT,
    medicamentos TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Citas
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    -- RESTRICT: no se puede eliminar un médico con citas (TC-48)
    doctor_id INTEGER REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_hora TIMESTAMP NOT NULL,
    tipo VARCHAR(50) NOT NULL,  -- consulta, limpieza, procedimiento, revision, urgencia
    procedimiento VARCHAR(100),
    costo DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (costo >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'programada'
        CHECK (estado IN ('programada', 'en_curso', 'completada', 'cancelada')),
    notas TEXT,
    duracion_minutos INTEGER NOT NULL DEFAULT 30 CHECK (duracion_minutos > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catálogo de procedimientos
CREATE TABLE procedimientos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    costo DECIMAL(10,2) NOT NULL,
    duracion_estimada INTEGER DEFAULT 30,
    categoria VARCHAR(50)
);

-- Procedimientos realizados / por realizar a cada paciente (generan adeudo)
CREATE TABLE procedimientos_paciente (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    procedimiento_id INTEGER REFERENCES procedimientos(id) ON DELETE SET NULL,
    cita_id INTEGER REFERENCES citas(id) ON DELETE SET NULL,
    diente_numero INTEGER CHECK (diente_numero BETWEEN 1 AND 32),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'en_proceso', 'completado')),
    fecha_realizacion DATE,
    notas TEXT,
    costo DECIMAL(10,2) NOT NULL CHECK (costo >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Estado de cada pieza dental (numeración universal 1-32)
CREATE TABLE estados_dentales (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    diente_numero INTEGER NOT NULL CHECK (diente_numero >= 1 AND diente_numero <= 32),
    estado VARCHAR(50) NOT NULL DEFAULT 'sano',
    tratamiento_actual INTEGER REFERENCES procedimientos_paciente(id) ON DELETE SET NULL,
    notas TEXT,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (paciente_id, diente_numero)
);

-- Pagos (un pago corresponde a un solo procedimiento, RN08)
CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    procedimiento_id INTEGER REFERENCES procedimientos_paciente(id) ON DELETE SET NULL,
    monto DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    metodo_pago VARCHAR(50) NOT NULL,
    fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE,
    concepto VARCHAR(100),
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historial médico
CREATE TABLE historial_medico (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    fecha DATE DEFAULT CURRENT_DATE,
    tipo VARCHAR(50),
    descripcion TEXT,
    observaciones TEXT,
    realizado_por INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cuentas de acceso al sistema
CREATE TABLE usuarios_sistema (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    -- Hash SHA-256 en hexadecimal, nunca texto plano (RNF06)
    password CHAR(64) NOT NULL
        CONSTRAINT usuarios_sistema_password_sha256 CHECK (password ~ '^[0-9a-f]{64}$'),
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(100),
    es_superadmin BOOLEAN NOT NULL DEFAULT false,
    permisos JSONB NOT NULL DEFAULT '{"menus": ["dashboard"], "puede_eliminar": false}',
    medico_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_pacientes_nombre ON pacientes(nombre, apellidos);
CREATE INDEX idx_citas_fecha ON citas(fecha_hora);
CREATE INDEX idx_citas_paciente ON citas(paciente_id);
CREATE INDEX idx_citas_doctor ON citas(doctor_id);
CREATE INDEX idx_citas_estado ON citas(estado);
CREATE INDEX idx_procedimientos_paciente ON procedimientos_paciente(paciente_id);
CREATE INDEX idx_estados_dentales_paciente ON estados_dentales(paciente_id);
CREATE INDEX idx_pagos_paciente ON pagos(paciente_id);
CREATE INDEX idx_pagos_procedimiento ON pagos(procedimiento_id);

-- Usuario administrador por defecto (contraseña: admin123)
INSERT INTO usuarios_sistema (username, password, nombre, puesto, es_superadmin, permisos)
VALUES ('admin',
        '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        'Administrador', 'Super Usuario', true,
        '{"menus": ["dashboard", "citas", "pacientes", "expedientes", "odontograma", "adeudos", "medicos", "usuarios"], "puede_eliminar": true}');
