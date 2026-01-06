-- Active: 1765317685704@@127.0.0.1@5432@sistema_dental
-- Base de datos para Sistema Dental
CREATE DATABASE sistema_dental;

\c sistema_dental;

-- Tabla de Dentistas/Usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    especialidad VARCHAR(100),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Pacientes
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    curp VARCHAR(18) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    edad INTEGER,
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

-- Tabla de Citas
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_hora TIMESTAMP NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- 'consulta', 'limpieza', 'procedimiento'
    procedimiento VARCHAR(100),
    costo DECIMAL(10,2) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'programada', -- 'programada', 'en_curso', 'completada', 'cancelada'
    notas TEXT,
    duracion_minutos INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Procedimientos
CREATE TABLE procedimientos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    costo DECIMAL(10,2) NOT NULL,
    duracion_estimada INTEGER DEFAULT 30,
    categoria VARCHAR(50) -- 'limpieza', 'restauracion', 'extraccion', etc.
);

-- Tabla de Procedimientos del Paciente
CREATE TABLE procedimientos_paciente (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    procedimiento_id INTEGER REFERENCES procedimientos(id) ON DELETE SET NULL,
    cita_id INTEGER REFERENCES citas(id) ON DELETE SET NULL,
    diente_numero INTEGER, -- Número del diente (1-32)
    estado VARCHAR(20) DEFAULT 'pendiente', -- 'pendiente', 'en_proceso', 'completado'
    fecha_realizacion DATE,
    notas TEXT,
    costo DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Estados Dentales
CREATE TABLE estados_dentales (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    diente_numero INTEGER NOT NULL CHECK (diente_numero >= 1 AND diente_numero <= 32),
    estado VARCHAR(50) DEFAULT 'sano', -- 'sano', 'cariado', 'obturado', 'extraido', 'en_tratamiento'
    tratamiento_actual INTEGER REFERENCES procedimientos_paciente(id) ON DELETE SET NULL,
    notas TEXT,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(paciente_id, diente_numero)
);

-- Tabla de Pagos
CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    procedimiento_id INTEGER REFERENCES procedimientos_paciente(id) ON DELETE SET NULL,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50), -- 'efectivo', 'tarjeta', 'transferencia'
    fecha_pago DATE DEFAULT CURRENT_DATE,
    concepto VARCHAR(100),
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Historial Médico
CREATE TABLE historial_medico (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id) ON DELETE CASCADE,
    fecha DATE DEFAULT CURRENT_DATE,
    tipo VARCHAR(50), -- 'consulta', 'procedimiento', 'observacion'
    descripcion TEXT,
    observaciones TEXT,
    realizado_por INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Usuarios del Sistema (para Login)
CREATE TABLE usuarios_sistema (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(100),
    es_superadmin BOOLEAN DEFAULT false,
    permisos JSONB DEFAULT '{"menus": ["dashboard"], "puede_eliminar": false}',
    medico_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_pacientes_curp ON pacientes(curp);
CREATE INDEX idx_pacientes_nombre ON pacientes(nombre, apellidos);
CREATE INDEX idx_citas_fecha ON citas(fecha_hora);
CREATE INDEX idx_citas_paciente ON citas(paciente_id);
CREATE INDEX idx_citas_estado ON citas(estado);
CREATE INDEX idx_procedimientos_paciente ON procedimientos_paciente(paciente_id);
CREATE INDEX idx_estados_dentales_paciente ON estados_dentales(paciente_id);
CREATE INDEX idx_pagos_paciente ON pagos(paciente_id);

-- Usuario administrador por defecto (password: admin123)
INSERT INTO usuarios_sistema (username, password, nombre, puesto, es_superadmin, permisos)
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrador', 'Super Usuario', true, '{"menus": ["dashboard", "citas", "pacientes", "expedientes", "odontograma", "adeudos", "medicos", "usuarios"], "puede_eliminar": true}');