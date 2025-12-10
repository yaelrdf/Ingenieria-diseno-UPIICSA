-- Active: 1765317685704@@127.0.0.1@5432@sistema_dental
-- Script de datos de prueba para Sistema Dental
-- Ejecutar después de crear la base de datos

BEGIN;

ABORT

-- 1. Limpiar tablas (opcional, descomentar si necesitas reiniciar)

TRUNCATE TABLE pagos CASCADE;
TRUNCATE TABLE estados_dentales CASCADE;
TRUNCATE TABLE procedimientos_paciente CASCADE;
TRUNCATE TABLE historial_medico CASCADE;
TRUNCATE TABLE citas CASCADE;
TRUNCATE TABLE pacientes CASCADE;
TRUNCATE TABLE procedimientos CASCADE;
TRUNCATE TABLE usuarios CASCADE;

-- Script de inserción de datos de ejemplo para Sistema Dental
-- Asegúrate de ejecutar primero el script create_database.sql

\c sistema_dental;

-- ============================================
-- 1. INSERTAR USUARIOS (Dentistas)
-- ============================================
INSERT INTO usuarios (nombre, email, telefono, especialidad, activo) VALUES 
('Dr. Juan Pérez', 'juan.perez@clinica.com', '5551234567', 'Ortodoncista', true),
('Dra. María García', 'maria.garcia@clinica.com', '5551234568', 'Periodoncista', true),
('Dr. Carlos Rodríguez', 'carlos.rodriguez@clinica.com', '5551234569', 'Cirujano Maxilofacial', true),
('Dra. Ana Martínez', 'ana.martinez@clinica.com', '5551234570', 'Endodoncista', true),
('Dr. Luis Hernández', 'luis.hernandez@clinica.com', '5551234571', 'Odontología General', true);

-- ============================================
-- 2. INSERTAR PROCEDIMIENTOS
-- ============================================
INSERT INTO procedimientos (nombre, descripcion, costo, duracion_estimada, categoria) VALUES
('Consulta inicial', 'Consulta y evaluación inicial del paciente', 500.00, 30, 'consulta'),
('Limpieza dental', 'Limpieza profesional y profilaxis', 800.00, 45, 'limpieza'),
('Obturación (empaste)', 'Tratamiento de caries con resina', 1200.00, 60, 'restauracion'),
('Extracción simple', 'Extracción de pieza dental simple', 1500.00, 45, 'extraccion'),
('Extracción compleja', 'Extracción quirúrgica de pieza dental', 2500.00, 90, 'extraccion'),
('Endodoncia', 'Tratamiento de conducto radicular', 3000.00, 120, 'endodoncia'),
('Corona dental', 'Colocación de corona de porcelana', 4500.00, 90, 'protesis'),
('Blanqueamiento dental', 'Blanqueamiento profesional', 2000.00, 60, 'estetica'),
('Ortodoncia (mensual)', 'Pago mensual de tratamiento ortodóntico', 1800.00, 45, 'ortodoncia'),
('Implante dental', 'Colocación de implante osteointegrado', 8000.00, 120, 'implante'),
('Puente dental', 'Puente de 3 piezas', 6000.00, 120, 'protesis'),
('Radiografía panorámica', 'Radiografía completa de la boca', 400.00, 15, 'diagnostico');

-- ============================================
-- 3. INSERTAR PACIENTES
-- ============================================
INSERT INTO pacientes (curp, nombre, apellidos, fecha_nacimiento, edad, genero, telefono, email, direccion, alergias, enfermedades_cronicas, medicamentos, observaciones) VALUES 
('MERA850315HDFRND09', 'Roberto', 'Méndez Ramírez', '1985-03-15', 39, 'Masculino', '5552345678', 'roberto.mendez@email.com', 'Av. Insurgentes Sur 1234, CDMX', 'Penicilina', 'Ninguna', 'Ninguno', 'Paciente regular, muy puntual'),
('LOGM900520MDFPNR03', 'Gabriela', 'López Martínez', '1990-05-20', 34, 'Femenino', '5552345679', 'gabriela.lopez@email.com', 'Calle Reforma 456, CDMX', 'Ninguna', 'Diabetes tipo 2', 'Metformina', 'Requiere citas temprano por la mañana'),
('SACP780810HDFLRR08', 'Pedro', 'Sánchez Cruz', '1978-08-10', 46, 'Masculino', '5552345680', 'pedro.sanchez@email.com', 'Col. Roma Norte, CDMX', 'Látex', 'Hipertensión', 'Losartán', 'Nervioso durante procedimientos'),
('ROJA920225MDFSMN04', 'Ana', 'Rojas Jiménez', '1992-02-25', 32, 'Femenino', '5552345681', 'ana.rojas@email.com', 'Col. Condesa, CDMX', 'Ninguna', 'Ninguna', 'Ninguno', 'Excelente higiene bucal'),
('VASL881112HDFLNR02', 'Luis', 'Vargas Sánchez', '1988-11-12', 36, 'Masculino', '5552345682', 'luis.vargas@email.com', 'Col. Polanco, CDMX', 'Anestesia local', 'Ninguna', 'Ninguno', 'Usar anestesia tipo mepivacaína'),
('HEMA950430MDFRRN01', 'Mariana', 'Hernández Morales', '1995-04-30', 29, 'Femenino', '5552345683', 'mariana.hernandez@email.com', 'Col. Del Valle, CDMX', 'Ninguna', 'Asma', 'Salbutamol', 'Paciente nueva'),
('GAPE870918HDFRRL05', 'Eduardo', 'García Pérez', '1987-09-18', 37, 'Masculino', '5552345684', 'eduardo.garcia@email.com', 'Col. Coyoacán, CDMX', 'Ibuprofeno', 'Ninguna', 'Paracetamol', 'Fumador, requiere limpiezas frecuentes'),
('TOMA931205MDFRRN06', 'Mónica', 'Torres Martínez', '1993-12-05', 31, 'Femenino', '5552345685', 'monica.torres@email.com', 'Col. Narvarte, CDMX', 'Ninguna', 'Ninguna', 'Ninguno', 'En tratamiento ortodóntico'),
('CASI800722HDFSLN07', 'Ignacio', 'Castro Silva', '1980-07-22', 44, 'Masculino', '5552345686', 'ignacio.castro@email.com', 'Col. San Rafael, CDMX', 'Ninguna', 'Gastritis crónica', 'Omeprazol', 'Evitar medicamentos irritantes'),
('RUMA970304MDFBZR08', 'Adriana', 'Rubio Méndez', '1997-03-04', 27, 'Femenino', '5552345687', 'adriana.rubio@email.com', 'Col. Juárez, CDMX', 'Ninguna', 'Ninguna', 'Ninguno', 'Estudiante, horarios flexibles');

-- ============================================
-- 4. INSERTAR CITAS
-- ============================================
INSERT INTO citas (paciente_id, doctor_id, fecha_hora, tipo, procedimiento, estado, notas, duracion_minutos) VALUES 
-- Citas completadas (pasadas)
(1, 1, '2024-11-15 09:00:00', 'consulta', 'Consulta inicial', 'completada', 'Primera consulta, requiere limpieza', 30),
(1, 2, '2024-11-22 10:00:00', 'limpieza', 'Limpieza dental', 'completada', 'Limpieza realizada sin complicaciones', 45),
(2, 3, '2024-11-18 11:00:00', 'consulta', 'Consulta inicial', 'completada', 'Evaluación general', 30),
(3, 1, '2024-11-20 14:00:00', 'procedimiento', 'Obturación', 'completada', 'Obturación en diente 16', 60),
(4, 4, '2024-11-25 09:30:00', 'consulta', 'Consulta inicial', 'completada', 'Paciente nueva, todo en orden', 30),
(5, 2, '2024-11-28 15:00:00', 'procedimiento', 'Extracción simple', 'completada', 'Extracción de molar 38', 45),

-- Citas próximas (programadas)
(6, 1, '2024-12-10 10:00:00', 'consulta', 'Consulta inicial', 'programada', 'Primera visita', 30),
(7, 2, '2024-12-11 11:00:00', 'limpieza', 'Limpieza dental', 'programada', 'Limpieza semestral', 45),
(8, 1, '2024-12-12 09:00:00', 'procedimiento', 'Ajuste ortodoncia', 'programada', 'Revisión mensual de brackets', 45),
(9, 3, '2024-12-13 14:00:00', 'consulta', 'Consulta de seguimiento', 'programada', 'Revisar gastritis antes de procedimiento', 30),
(10, 4, '2024-12-14 16:00:00', 'procedimiento', 'Endodoncia', 'programada', 'Tratamiento de conducto en diente 26', 120),
(2, 2, '2024-12-16 10:00:00', 'procedimiento', 'Obturación', 'programada', 'Tratar caries en diente 14', 60),

-- Cita cancelada
(3, 1, '2024-11-30 15:00:00', 'limpieza', 'Limpieza dental', 'cancelada', 'Paciente canceló por motivos personales', 45);

-- ============================================
-- 5. INSERTAR PROCEDIMIENTOS DEL PACIENTE
-- ============================================
INSERT INTO procedimientos_paciente (paciente_id, procedimiento_id, cita_id, diente_numero, estado, fecha_realizacion, notas, costo) VALUES 
-- Procedimientos completados
(1, 1, 1, NULL, 'completado', '2024-11-15', 'Consulta inicial realizada', 500.00),
(1, 2, 2, NULL, 'completado', '2024-11-22', 'Limpieza completa', 800.00),
(2, 1, 3, NULL, 'completado', '2024-11-18', 'Evaluación general', 500.00),
(3, 3, 4, 16, 'completado', '2024-11-20', 'Obturación con resina en molar superior', 1200.00),
(4, 1, 5, NULL, 'completado', '2024-11-25', 'Primera consulta', 500.00),
(5, 4, 6, 38, 'completado', '2024-11-28', 'Extracción de tercer molar', 1500.00),

-- Procedimientos pendientes
(6, 1, 7, NULL, 'pendiente', NULL, 'Consulta inicial programada', 500.00),
(7, 2, 8, NULL, 'pendiente', NULL, 'Limpieza programada', 800.00),
(8, 9, 9, NULL, 'pendiente', NULL, 'Ajuste mensual de ortodoncia', 1800.00),
(9, 1, 10, NULL, 'pendiente', NULL, 'Consulta de seguimiento', 500.00),
(10, 6, 11, 26, 'pendiente', NULL, 'Endodoncia programada', 3000.00),
(2, 3, 12, 14, 'pendiente', NULL, 'Obturación pendiente', 1200.00);

-- ============================================
-- 6. INSERTAR ESTADOS DENTALES
-- ============================================
-- Para paciente 1 (Roberto)
INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas) VALUES 
(1, 16, 'sano', 'Buen estado general'),
(1, 17, 'sano', 'Buen estado general'),
(1, 18, 'sano', 'Buen estado general');

-- Para paciente 3 (Pedro)
INSERT INTO estados_dentales (paciente_id, diente_numero, estado, tratamiento_actual, notas) VALUES 
(3, 16, 'obturado', 4, 'Obturación reciente'),
(3, 15, 'cariado', NULL, 'Requiere tratamiento'),
(3, 26, 'sano', NULL, 'Buen estado');

-- Para paciente 5 (Luis)
INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas) VALUES 
(5, 38, 'extraido', 'Extracción reciente'),
(5, 37, 'sano', 'Buen estado'),
(5, 36, 'sano', 'Buen estado');

-- Para paciente 8 (Mónica - en ortodoncia)
INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas) VALUES 
(8, 11, 'en_tratamiento', 'Ortodoncia activa'),
(8, 12, 'en_tratamiento', 'Ortodoncia activa'),
(8, 21, 'en_tratamiento', 'Ortodoncia activa'),
(8, 22, 'en_tratamiento', 'Ortodoncia activa');

-- ============================================
-- 7. INSERTAR PAGOS
-- ============================================
INSERT INTO pagos (paciente_id, procedimiento_id, monto, metodo_pago, fecha_pago, concepto, notas) VALUES 
-- Pagos completados
(1, 1, 500.00, 'efectivo', '2024-11-15', 'Consulta inicial', 'Pago completo'),
(1, 2, 800.00, 'tarjeta', '2024-11-22', 'Limpieza dental', 'Pago con tarjeta débito'),
(2, 3, 500.00, 'transferencia', '2024-11-18', 'Consulta inicial', 'Transferencia bancaria'),
(3, 4, 1200.00, 'efectivo', '2024-11-20', 'Obturación', 'Pago completo en efectivo'),
(4, 5, 500.00, 'tarjeta', '2024-11-25', 'Consulta inicial', 'Tarjeta de crédito'),
(5, 6, 1500.00, 'efectivo', '2024-11-28', 'Extracción dental', 'Pago completo'),

-- Pagos anticipados
(6, 7, 500.00, 'transferencia', '2024-12-05', 'Anticipo consulta', 'Pago anticipado'),
(10, 11, 1500.00, 'tarjeta', '2024-12-06', 'Anticipo endodoncia', 'Pago parcial del tratamiento');

-- ============================================
-- 8. INSERTAR HISTORIAL MÉDICO
-- ============================================
INSERT INTO historial_medico (paciente_id, fecha, tipo, descripcion, observaciones, realizado_por) VALUES 
(1, '2024-11-15', 'consulta', 'Primera consulta - Evaluación general', 'Paciente presenta buena salud bucal general. Se recomienda limpieza profesional.', 1),
(1, '2024-11-22', 'procedimiento', 'Limpieza dental profesional realizada', 'Procedimiento sin complicaciones. Paciente tolera bien el tratamiento.', 2),
(2, '2024-11-18', 'consulta', 'Consulta inicial - Paciente diabética', 'Paciente con diabetes tipo 2 controlada. Se tomaron precauciones necesarias.', 3),
(3, '2024-11-20', 'procedimiento', 'Obturación en diente 16', 'Se realizó obturación con resina en molar superior derecho. Paciente presentó nerviosismo pero cooperó.', 1),
(4, '2024-11-25', 'consulta', 'Primera consulta - Excelente higiene', 'Paciente muestra excelente cuidado bucal. Sin problemas detectados.', 4),
(5, '2024-11-28', 'procedimiento', 'Extracción de tercer molar inferior derecho', 'Extracción simple sin complicaciones. Se usó mepivacaína por alergia a anestesia convencional.', 2),
(6, '2024-11-30', 'observacion', 'Primera visita programada', 'Paciente nueva con asma. Mantener inhalador disponible durante procedimientos.', 1),
(7, '2024-12-01', 'observacion', 'Paciente fumador', 'Se recomendó dejar de fumar para mejor salud bucal. Programar limpiezas cada 4 meses.', 2),
(8, '2024-12-02', 'observacion', 'Seguimiento de ortodoncia', 'Tratamiento ortodóntico progresando adecuadamente. Próximo ajuste en diciembre.', 1),
(9, '2024-12-03', 'observacion', 'Precaución por gastritis', 'Evitar medicamentos antiinflamatorios fuertes. Usar paracetamol si es necesario.', 3);

-- ============================================
-- VERIFICACIÓN DE DATOS INSERTADOS
-- ============================================
SELECT 'Usuarios insertados:' AS tabla, COUNT(*) AS total FROM usuarios
UNION ALL
SELECT 'Procedimientos insertados:', COUNT(*) FROM procedimientos
UNION ALL
SELECT 'Pacientes insertados:', COUNT(*) FROM pacientes
UNION ALL
SELECT 'Citas insertadas:', COUNT(*) FROM citas
UNION ALL
SELECT 'Procedimientos de pacientes:', COUNT(*) FROM procedimientos_paciente
UNION ALL
SELECT 'Estados dentales:', COUNT(*) FROM estados_dentales
UNION ALL
SELECT 'Pagos registrados:', COUNT(*) FROM pagos
UNION ALL
SELECT 'Registros de historial médico:', COUNT(*) FROM historial_medico;