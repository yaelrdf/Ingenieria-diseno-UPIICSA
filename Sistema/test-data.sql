-- Active: 1765317685704@@127.0.0.1@5432@sistema_dental
-- Script de datos de prueba para Sistema Dental
-- Ejecutar después de crear la base de datos

BEGIN;

ABORT

COMMIT

-- Script de inserción de datos de ejemplo para Sistema Dental
-- Asegúrate de ejecutar primero el script create_database.sql

\c sistema_dental;

-- ============================================
-- 1. LIMPIAR DATOS EXISTENTES (OPCIONAL)
-- ============================================
-- Descomenta estas líneas si necesitas limpiar la base de datos primero
-- TRUNCATE TABLE historial_medico CASCADE;
-- TRUNCATE TABLE pagos CASCADE;
-- TRUNCATE TABLE estados_dentales CASCADE;
-- TRUNCATE TABLE procedimientos_paciente CASCADE;
-- TRUNCATE TABLE citas CASCADE;
-- TRUNCATE TABLE pacientes CASCADE;
-- TRUNCATE TABLE procedimientos CASCADE;
-- TRUNCATE TABLE usuarios CASCADE;

-- ============================================
-- 2. INSERTAR USUARIOS (Dentistas)
-- ============================================
INSERT INTO usuarios (nombre, email, telefono, especialidad, activo) VALUES 
('Dr. Juan Pérez', 'juan.perez@clinica.com', '5551234567', 'Ortodoncista', true),
('Dra. María García', 'maria.garcia@clinica.com', '5551234568', 'Periodoncista', true),
('Dr. Carlos Rodríguez', 'carlos.rodriguez@clinica.com', '5551234569', 'Cirujano Maxilofacial', true),
('Dra. Ana Martínez', 'ana.martinez@clinica.com', '5551234570', 'Endodoncista', true),
('Dr. Luis Hernández', 'luis.hernandez@clinica.com', '5551234571', 'Odontología General', true);

-- ============================================
-- 3. INSERTAR PROCEDIMIENTOS
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
-- 4. INSERTAR PACIENTES
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
-- 5. INSERTAR CITAS
-- ============================================
-- Usando subqueries para obtener los IDs correctos
INSERT INTO citas (paciente_id, doctor_id, fecha_hora, tipo, procedimiento, estado, notas, duracion_minutos) VALUES 
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com'), '2024-11-15 09:00:00', 'consulta', 'Consulta inicial', 'completada', 'Primera consulta, requiere limpieza', 30),
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com'), '2024-11-22 10:00:00', 'limpieza', 'Limpieza dental', 'completada', 'Limpieza realizada sin complicaciones', 45),
((SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03'), (SELECT id FROM usuarios WHERE email = 'carlos.rodriguez@clinica.com'), '2024-11-18 11:00:00', 'consulta', 'Consulta inicial', 'completada', 'Evaluación general', 30),
((SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com'), '2024-11-20 14:00:00', 'procedimiento', 'Obturación', 'completada', 'Obturación en diente 16', 60),
((SELECT id FROM pacientes WHERE curp = 'ROJA920225MDFSMN04'), (SELECT id FROM usuarios WHERE email = 'ana.martinez@clinica.com'), '2024-11-25 09:30:00', 'consulta', 'Consulta inicial', 'completada', 'Paciente nueva, todo en orden', 30),
((SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'), (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com'), '2024-11-28 15:00:00', 'procedimiento', 'Extracción simple', 'completada', 'Extracción de molar 38', 45),

((SELECT id FROM pacientes WHERE curp = 'HEMA950430MDFRRN01'), (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com'), '2024-12-10 10:00:00', 'consulta', 'Consulta inicial', 'programada', 'Primera visita', 30),
((SELECT id FROM pacientes WHERE curp = 'GAPE870918HDFRRL05'), (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com'), '2024-12-11 11:00:00', 'limpieza', 'Limpieza dental', 'programada', 'Limpieza semestral', 45),
((SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com'), '2024-12-12 09:00:00', 'procedimiento', 'Ajuste ortodoncia', 'programada', 'Revisión mensual de brackets', 45),
((SELECT id FROM pacientes WHERE curp = 'CASI800722HDFSLN07'), (SELECT id FROM usuarios WHERE email = 'carlos.rodriguez@clinica.com'), '2024-12-13 14:00:00', 'consulta', 'Consulta de seguimiento', 'programada', 'Revisar gastritis antes de procedimiento', 30),
((SELECT id FROM pacientes WHERE curp = 'RUMA970304MDFBZR08'), (SELECT id FROM usuarios WHERE email = 'ana.martinez@clinica.com'), '2024-12-14 16:00:00', 'procedimiento', 'Endodoncia', 'programada', 'Tratamiento de conducto en diente 26', 120),
((SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03'), (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com'), '2024-12-16 10:00:00', 'procedimiento', 'Obturación', 'programada', 'Tratar caries en diente 14', 60),

((SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com'), '2024-11-30 15:00:00', 'limpieza', 'Limpieza dental', 'cancelada', 'Paciente canceló por motivos personales', 45);

-- ============================================
-- 6. INSERTAR PROCEDIMIENTOS DEL PACIENTE
-- ============================================
INSERT INTO procedimientos_paciente (paciente_id, procedimiento_id, cita_id, diente_numero, estado, fecha_realizacion, notas, costo) VALUES 
-- Procedimientos completados
(
  (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Consulta inicial'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09') AND fecha_hora = '2024-11-15 09:00:00'),
  NULL, 'completado', '2024-11-15', 'Consulta inicial realizada', 500.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Limpieza dental'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09') AND fecha_hora = '2024-11-22 10:00:00'),
  NULL, 'completado', '2024-11-22', 'Limpieza completa', 800.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Consulta inicial'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03') AND fecha_hora = '2024-11-18 11:00:00'),
  NULL, 'completado', '2024-11-18', 'Evaluación general', 500.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Obturación (empaste)'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08') AND fecha_hora = '2024-11-20 14:00:00'),
  16, 'completado', '2024-11-20', 'Obturación con resina en molar superior', 1200.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'ROJA920225MDFSMN04'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Consulta inicial'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'ROJA920225MDFSMN04') AND fecha_hora = '2024-11-25 09:30:00'),
  NULL, 'completado', '2024-11-25', 'Primera consulta', 500.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Extracción simple'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02') AND fecha_hora = '2024-11-28 15:00:00'),
  38, 'completado', '2024-11-28', 'Extracción de tercer molar', 1500.00
),

(
  (SELECT id FROM pacientes WHERE curp = 'HEMA950430MDFRRN01'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Consulta inicial'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'HEMA950430MDFRRN01') AND fecha_hora = '2024-12-10 10:00:00'),
  NULL, 'pendiente', NULL, 'Consulta inicial programada', 500.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'GAPE870918HDFRRL05'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Limpieza dental'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'GAPE870918HDFRRL05') AND fecha_hora = '2024-12-11 11:00:00'),
  NULL, 'pendiente', NULL, 'Limpieza programada', 800.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Ortodoncia (mensual)'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06') AND fecha_hora = '2024-12-12 09:00:00'),
  NULL, 'pendiente', NULL, 'Ajuste mensual de ortodoncia', 1800.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'CASI800722HDFSLN07'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Consulta inicial'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'CASI800722HDFSLN07') AND fecha_hora = '2024-12-13 14:00:00'),
  NULL, 'pendiente', NULL, 'Consulta de seguimiento', 500.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'RUMA970304MDFBZR08'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Endodoncia'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'RUMA970304MDFBZR08') AND fecha_hora = '2024-12-14 16:00:00'),
  26, 'pendiente', NULL, 'Endodoncia programada', 3000.00
),
(
  (SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03'), 
  (SELECT id FROM procedimientos WHERE nombre = 'Obturación (empaste)'), 
  (SELECT id FROM citas WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03') AND fecha_hora = '2024-12-16 10:00:00'),
  14, 'pendiente', NULL, 'Obturación pendiente', 1200.00
);

-- ============================================
-- 7. INSERTAR ESTADOS DENTALES
-- ============================================
INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas) VALUES 
-- Para Roberto (MERA850315HDFRND09)
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), 16, 'sano', 'Buen estado general'),
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), 17, 'sano', 'Buen estado general'),
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), 18, 'sano', 'Buen estado general'),

((SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), 16, 'obturado', 'Obturación reciente'),
((SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), 15, 'cariado', 'Requiere tratamiento'),
((SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), 26, 'sano', 'Buen estado'),

((SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'), 38, 'extraido', 'Extracción reciente'),
((SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'), 37, 'sano', 'Buen estado'),
((SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'), 36, 'sano', 'Buen estado'),

((SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), 11, 'en_tratamiento', 'Ortodoncia activa'),
((SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), 12, 'en_tratamiento', 'Ortodoncia activa'),
((SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), 21, 'en_tratamiento', 'Ortodoncia activa'),
((SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), 22, 'en_tratamiento', 'Ortodoncia activa');

-- ============================================
-- 8. INSERTAR PAGOS
-- ============================================
INSERT INTO pagos (paciente_id, procedimiento_id, monto, metodo_pago, fecha_pago, concepto, notas) VALUES 
(
  (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09') AND fecha_realizacion = '2024-11-15' LIMIT 1),
  500.00, 'efectivo', '2024-11-15', 'Consulta inicial', 'Pago completo'
),
(
  (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09') AND fecha_realizacion = '2024-11-22' LIMIT 1),
  800.00, 'tarjeta', '2024-11-22', 'Limpieza dental', 'Pago con tarjeta débito'
),
(
  (SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03') AND fecha_realizacion = '2024-11-18' LIMIT 1),
  500.00, 'transferencia', '2024-11-18', 'Consulta inicial', 'Transferencia bancaria'
),
(
  (SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08') AND fecha_realizacion = '2024-11-20' LIMIT 1),
  1200.00, 'efectivo', '2024-11-20', 'Obturación', 'Pago completo en efectivo'
),
(
  (SELECT id FROM pacientes WHERE curp = 'ROJA920225MDFSMN04'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'ROJA920225MDFSMN04') AND fecha_realizacion = '2024-11-25' LIMIT 1),
  500.00, 'tarjeta', '2024-11-25', 'Consulta inicial', 'Tarjeta de crédito'
),
(
  (SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02') AND fecha_realizacion = '2024-11-28' LIMIT 1),
  1500.00, 'efectivo', '2024-11-28', 'Extracción dental', 'Pago completo'
),

(
  (SELECT id FROM pacientes WHERE curp = 'HEMA950430MDFRRN01'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'HEMA950430MDFRRN01') LIMIT 1),
  500.00, 'transferencia', '2024-12-05', 'Anticipo consulta', 'Pago anticipado'
),
(
  (SELECT id FROM pacientes WHERE curp = 'RUMA970304MDFBZR08'),
  (SELECT id FROM procedimientos_paciente WHERE paciente_id = (SELECT id FROM pacientes WHERE curp = 'RUMA970304MDFBZR08') LIMIT 1),
  1500.00, 'tarjeta', '2024-12-06', 'Anticipo endodoncia', 'Pago parcial del tratamiento'
);

-- ============================================
-- 9. INSERTAR HISTORIAL MÉDICO
-- ============================================
INSERT INTO historial_medico (paciente_id, fecha, tipo, descripcion, observaciones, realizado_por) VALUES 
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), '2024-11-15', 'consulta', 'Primera consulta - Evaluación general', 'Paciente presenta buena salud bucal general. Se recomienda limpieza profesional.', (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'MERA850315HDFRND09'), '2024-11-22', 'procedimiento', 'Limpieza dental profesional realizada', 'Procedimiento sin complicaciones. Paciente tolera bien el tratamiento.', (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'LOGM900520MDFPNR03'), '2024-11-18', 'consulta', 'Consulta inicial - Paciente diabética', 'Paciente con diabetes tipo 2 controlada. Se tomaron precauciones necesarias.', (SELECT id FROM usuarios WHERE email = 'carlos.rodriguez@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'SACP780810HDFLRR08'), '2024-11-20', 'procedimiento', 'Obturación en diente 16', 'Se realizó obturación con resina en molar superior derecho. Paciente presentó nerviosismo pero cooperó.', (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'ROJA920225MDFSMN04'), '2024-11-25', 'consulta', 'Primera consulta - Excelente higiene', 'Paciente muestra excelente cuidado bucal. Sin problemas detectados.', (SELECT id FROM usuarios WHERE email = 'ana.martinez@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'VASL881112HDFLNR02'), '2024-11-28', 'procedimiento', 'Extracción de tercer molar inferior derecho', 'Extracción simple sin complicaciones. Se usó mepivacaína por alergia a anestesia convencional.', (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'HEMA950430MDFRRN01'), '2024-11-30', 'observacion', 'Primera visita programada', 'Paciente nueva con asma. Mantener inhalador disponible durante procedimientos.', (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'GAPE870918HDFRRL05'), '2024-12-01', 'observacion', 'Paciente fumador', 'Se recomendó dejar de fumar para mejor salud bucal. Programar limpiezas cada 4 meses.', (SELECT id FROM usuarios WHERE email = 'maria.garcia@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'TOMA931205MDFRRN06'), '2024-12-02', 'observacion', 'Seguimiento de ortodoncia', 'Tratamiento ortodóntico progresando adecuadamente. Próximo ajuste en diciembre.', (SELECT id FROM usuarios WHERE email = 'juan.perez@clinica.com')),
((SELECT id FROM pacientes WHERE curp = 'CASI800722HDFSLN07'), '2024-12-03', 'observacion', 'Precaución por gastritis', 'Evitar medicamentos antiinflamatorios fuertes. Usar paracetamol si es necesario.', (SELECT id FROM usuarios WHERE email = 'carlos.rodriguez@clinica.com'));

-- ============================================
-- 10. VERIFICACIÓN DE DATOS INSERTADOS
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