-- =====================================================================
-- Sonrisa Perfecta v1.1.0 - Datos de muestra
-- Las fechas son relativas al día de creación de la base de datos, de modo
-- que siempre existen citas pasadas, del día y futuras.
-- Cubre las precondiciones de la matriz de pruebas:
--   * Médico activo sin citas (TC-47) y médicos con citas (TC-48)
--   * Médico inactivo (TC-55)
--   * Cita sin médico asignado (TC-54) y cita cancelada (TC-58)
--   * Procedimientos completados con saldo, liquidados y en proceso (TC-74 a TC-85)
-- =====================================================================

BEGIN;

-- Funciones auxiliares (solo viven durante esta sesión)
CREATE FUNCTION pg_temp.pac(p_curp text) RETURNS int
    LANGUAGE sql AS $$ SELECT id FROM pacientes WHERE curp = p_curp $$;
CREATE FUNCTION pg_temp.med(p_email text) RETURNS int
    LANGUAGE sql AS $$ SELECT id FROM usuarios WHERE email = p_email $$;
CREATE FUNCTION pg_temp.proc(p_nombre text) RETURNS int
    LANGUAGE sql AS $$ SELECT id FROM procedimientos WHERE nombre = p_nombre $$;
CREATE FUNCTION pg_temp.cita(p_curp text, p_fecha timestamp) RETURNS int
    LANGUAGE sql AS $$ SELECT id FROM citas WHERE paciente_id = pg_temp.pac(p_curp) AND fecha_hora = p_fecha $$;
CREATE FUNCTION pg_temp.pp(p_curp text, p_nombre text) RETURNS int
    LANGUAGE sql AS $$ SELECT id FROM procedimientos_paciente
                       WHERE paciente_id = pg_temp.pac(p_curp) AND procedimiento_id = pg_temp.proc(p_nombre)
                       ORDER BY id LIMIT 1 $$;

-- ---------------------------------------------------------------------
-- Médicos
-- ---------------------------------------------------------------------
INSERT INTO usuarios (nombre, email, telefono, especialidad, activo) VALUES
('Dr. Ángel Domínguez Ruiz',   'angel.dominguez@sonrisaperfecta.mx', '5551234501', 'Odontología General', true),
('Dra. María García López',    'maria.garcia@sonrisaperfecta.mx',    '5551234502', 'Ortodoncia', true),
('Dr. Carlos Rodríguez Vega',  'carlos.rodriguez@sonrisaperfecta.mx', '5551234503', 'Cirugía Maxilofacial', true),
('Dra. Ana Martínez Soto',     'ana.martinez@sonrisaperfecta.mx',    '5551234504', 'Endodoncia', true),
('Dra. Sofía Navarro Ruiz',    'sofia.navarro@sonrisaperfecta.mx',   '5551234505', 'Periodoncia', true),
('Dr. Jorge Salas Medina',     'jorge.salas@sonrisaperfecta.mx',     '5551234506', 'Odontopediatría', false);

-- ---------------------------------------------------------------------
-- Catálogo de procedimientos
-- ---------------------------------------------------------------------
INSERT INTO procedimientos (nombre, descripcion, costo, duracion_estimada, categoria) VALUES
('Consulta inicial',       'Consulta y evaluación inicial del paciente', 500.00, 30, 'consulta'),
('Limpieza dental',        'Limpieza profesional y profilaxis', 800.00, 45, 'limpieza'),
('Obturación (resina)',    'Tratamiento de caries con resina', 1200.00, 60, 'restauracion'),
('Extracción simple',      'Extracción de pieza dental simple', 1500.00, 45, 'extraccion'),
('Extracción quirúrgica',  'Extracción quirúrgica de pieza dental', 2500.00, 90, 'extraccion'),
('Endodoncia',             'Tratamiento de conductos radiculares', 3000.00, 120, 'endodoncia'),
('Corona de porcelana',    'Colocación de corona de porcelana', 4500.00, 90, 'protesis'),
('Blanqueamiento dental',  'Blanqueamiento profesional', 2000.00, 60, 'estetica'),
('Ortodoncia (mensual)',   'Ajuste mensual de tratamiento ortodóntico', 1800.00, 45, 'ortodoncia'),
('Implante dental',        'Colocación de implante osteointegrado', 8000.00, 120, 'implante'),
('Radiografía panorámica', 'Radiografía completa de la boca', 400.00, 15, 'diagnostico');

-- ---------------------------------------------------------------------
-- Pacientes
-- ---------------------------------------------------------------------
INSERT INTO pacientes (curp, nombre, apellidos, fecha_nacimiento, genero, telefono, email, direccion,
                       alergias, enfermedades_cronicas, medicamentos, observaciones) VALUES
('MERR850315HDFNMB09', 'Roberto',  'Méndez Ramírez',    '1985-03-15', 'Masculino', '5552345678', 'roberto.mendez@correo.mx',   'Av. Insurgentes Sur 1234, CDMX', 'Penicilina', NULL, NULL, 'Paciente regular, muy puntual.'),
('LOMG900520MDFPRB03', 'Gabriela', 'López Martínez',    '1990-05-20', 'Femenino',  '5552345679', 'gabriela.lopez@correo.mx',   'Calle Reforma 456, CDMX', NULL, 'Diabetes tipo 2', 'Metformina', 'Prefiere citas temprano por la mañana.'),
('SACP780810HDFNRD08', 'Pedro',    'Sánchez Cruz',      '1978-08-10', 'Masculino', '5552345680', 'pedro.sanchez@correo.mx',    'Col. Roma Norte, CDMX', 'Látex', 'Hipertensión', 'Losartán', 'Se pone nervioso durante los procedimientos.'),
('ROJA920225MDFJMN04', 'Ana',      'Rojas Jiménez',     '1992-02-25', 'Femenino',  '5552345681', 'ana.rojas@correo.mx',        'Col. Condesa, CDMX', NULL, NULL, NULL, 'Excelente higiene bucal.'),
('VASL881112HDFRNS02', 'Luis',     'Vargas Sánchez',    '1988-11-12', 'Masculino', '5552345682', NULL,                         'Col. Polanco, CDMX', 'Lidocaína', NULL, NULL, 'Usar anestesia tipo mepivacaína.'),
('HEMM950430MDFRRR01', 'Mariana',  'Hernández Morales', '1995-04-30', 'Femenino',  '5552345683', 'mariana.hernandez@correo.mx', 'Col. Del Valle, CDMX', NULL, 'Asma', 'Salbutamol', 'Mantener inhalador disponible.'),
('GAPE870918HDFRRD05', 'Eduardo',  'García Pérez',      '1987-09-18', 'Masculino', '5552345684', 'eduardo.garcia@correo.mx',   'Col. Coyoacán, CDMX', 'Ibuprofeno', NULL, 'Paracetamol', 'Fumador, requiere limpiezas frecuentes.'),
('TOMM931205MDFRRN06', 'Mónica',   'Torres Martínez',   '1993-12-05', 'Femenino',  '5552345685', 'monica.torres@correo.mx',    'Col. Narvarte, CDMX', NULL, NULL, NULL, 'En tratamiento ortodóntico.'),
('CASJ800722HDFSLN07', 'Juan',     'Castro Silva',      '1980-07-22', 'Masculino', NULL,         NULL,                         'Col. San Rafael, CDMX', NULL, 'Gastritis crónica', 'Omeprazol', 'Paciente de primera vez.'),
('RUMA970304MDFBND08', 'Adriana',  'Rubio Méndez',      '1997-03-04', 'Femenino',  '5552345687', 'adriana.rubio@correo.mx',    'Col. Juárez, CDMX', NULL, NULL, NULL, 'Estudiante, horarios flexibles.');

-- ---------------------------------------------------------------------
-- Citas
-- ---------------------------------------------------------------------
INSERT INTO citas (paciente_id, doctor_id, fecha_hora, tipo, procedimiento, estado, notas, duracion_minutos, costo) VALUES
-- Pasadas
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.med('angel.dominguez@sonrisaperfecta.mx'),  (CURRENT_DATE - 60) + TIME '09:00', 'consulta',      'Consulta inicial',            'completada', 'Primera consulta, requiere limpieza.', 30, 500),
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.med('maria.garcia@sonrisaperfecta.mx'),     (CURRENT_DATE - 45) + TIME '10:00', 'limpieza',      'Limpieza dental',             'completada', 'Sin complicaciones.', 45, 800),
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.med('carlos.rodriguez@sonrisaperfecta.mx'), (CURRENT_DATE - 40) + TIME '11:00', 'consulta',      'Consulta inicial',            'completada', 'Evaluación general.', 30, 500),
(pg_temp.pac('SACP780810HDFNRD08'), pg_temp.med('angel.dominguez@sonrisaperfecta.mx'),  (CURRENT_DATE - 30) + TIME '14:00', 'procedimiento', 'Obturación diente 14',        'completada', 'Obturación con resina.', 60, 1200),
(pg_temp.pac('VASL881112HDFRNS02'), pg_temp.med('carlos.rodriguez@sonrisaperfecta.mx'), (CURRENT_DATE - 25) + TIME '15:00', 'procedimiento', 'Extracción diente 17',        'completada', 'Extracción simple con mepivacaína.', 45, 1500),
(pg_temp.pac('RUMA970304MDFBND08'), pg_temp.med('ana.martinez@sonrisaperfecta.mx'),     (CURRENT_DATE - 20) + TIME '16:00', 'procedimiento', 'Endodoncia diente 19',        'completada', 'Tratamiento de conductos concluido.', 120, 3000),
(pg_temp.pac('GAPE870918HDFRRD05'), pg_temp.med('jorge.salas@sonrisaperfecta.mx'),      (CURRENT_DATE - 90) + TIME '10:00', 'limpieza',      'Limpieza dental',             'completada', 'Atendido antes de la baja del médico.', 45, 800),
(pg_temp.pac('TOMM931205MDFRRN06'), pg_temp.med('maria.garcia@sonrisaperfecta.mx'),     (CURRENT_DATE - 15) + TIME '09:00', 'procedimiento', 'Ajuste de ortodoncia',        'completada', 'Ajuste mensual de brackets.', 45, 1800),
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.med('ana.martinez@sonrisaperfecta.mx'),     (CURRENT_DATE - 5)  + TIME '10:00', 'procedimiento', 'Endodoncia diente 30 (1/2)',  'completada', 'Primera sesión; tratamiento en proceso.', 90, 0),
(pg_temp.pac('SACP780810HDFNRD08'), pg_temp.med('angel.dominguez@sonrisaperfecta.mx'),  (CURRENT_DATE - 10) + TIME '12:00', 'limpieza',      'Limpieza dental',             'cancelada',  'El paciente canceló por motivos personales.', 45, 800),
-- Del día
(pg_temp.pac('HEMM950430MDFRRR01'), pg_temp.med('angel.dominguez@sonrisaperfecta.mx'),  CURRENT_DATE + TIME '09:00', 'consulta',  'Revisión general',        'programada', NULL, 30, 500),
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.med('carlos.rodriguez@sonrisaperfecta.mx'), CURRENT_DATE + TIME '10:00', 'revision',  'Revisión de limpieza',    'en_curso',   NULL, 30, 0),
(pg_temp.pac('ROJA920225MDFJMN04'), pg_temp.med('maria.garcia@sonrisaperfecta.mx'),     CURRENT_DATE + TIME '11:30', 'limpieza',  'Limpieza dental',         'programada', NULL, 45, 800),
(pg_temp.pac('CASJ800722HDFSLN07'), NULL,                                               CURRENT_DATE + TIME '13:00', 'consulta',  'Valoración de primera vez', 'programada', 'Paciente de primera vez, sin médico asignado.', 30, 500),
-- Futuras
(pg_temp.pac('GAPE870918HDFRRD05'), pg_temp.med('angel.dominguez@sonrisaperfecta.mx'),  (CURRENT_DATE + 2)  + TIME '17:00', 'limpieza',      'Limpieza dental',            'programada', 'Limpieza cada 4 meses.', 45, 800),
(pg_temp.pac('RUMA970304MDFBND08'), pg_temp.med('ana.martinez@sonrisaperfecta.mx'),     (CURRENT_DATE + 3)  + TIME '16:00', 'revision',      'Revisión post-endodoncia',   'programada', NULL, 30, 0),
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.med('maria.garcia@sonrisaperfecta.mx'),     (CURRENT_DATE + 7)  + TIME '10:00', 'procedimiento', 'Obturación diente 3',        'programada', NULL, 60, 1200),
(pg_temp.pac('TOMM931205MDFRRN06'), pg_temp.med('maria.garcia@sonrisaperfecta.mx'),     (CURRENT_DATE + 14) + TIME '09:00', 'procedimiento', 'Ajuste de ortodoncia',       'programada', NULL, 45, 1800);

-- ---------------------------------------------------------------------
-- Procedimientos de pacientes (adeudos)
-- ---------------------------------------------------------------------
INSERT INTO procedimientos_paciente (paciente_id, procedimiento_id, cita_id, diente_numero, estado, fecha_realizacion, notas, costo) VALUES
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.proc('Consulta inicial'),     pg_temp.cita('MERR850315HDFNMB09', (CURRENT_DATE - 60) + TIME '09:00'), NULL, 'completado', CURRENT_DATE - 60, 'Consulta inicial', 500),
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.proc('Limpieza dental'),      pg_temp.cita('MERR850315HDFNMB09', (CURRENT_DATE - 45) + TIME '10:00'), NULL, 'completado', CURRENT_DATE - 45, 'Limpieza completa', 800),
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.proc('Consulta inicial'),     pg_temp.cita('LOMG900520MDFPRB03', (CURRENT_DATE - 40) + TIME '11:00'), NULL, 'completado', CURRENT_DATE - 40, 'Evaluación general', 500),
(pg_temp.pac('SACP780810HDFNRD08'), pg_temp.proc('Obturación (resina)'),  pg_temp.cita('SACP780810HDFNRD08', (CURRENT_DATE - 30) + TIME '14:00'), 14,   'completado', CURRENT_DATE - 30, 'Resina en premolar superior', 1200),
(pg_temp.pac('VASL881112HDFRNS02'), pg_temp.proc('Extracción simple'),    pg_temp.cita('VASL881112HDFRNS02', (CURRENT_DATE - 25) + TIME '15:00'), 17,   'completado', CURRENT_DATE - 25, 'Extracción de tercer molar', 1500),
(pg_temp.pac('RUMA970304MDFBND08'), pg_temp.proc('Endodoncia'),           pg_temp.cita('RUMA970304MDFBND08', (CURRENT_DATE - 20) + TIME '16:00'), 19,   'completado', CURRENT_DATE - 20, 'Endodoncia concluida', 3000),
(pg_temp.pac('GAPE870918HDFRRD05'), pg_temp.proc('Limpieza dental'),      pg_temp.cita('GAPE870918HDFRRD05', (CURRENT_DATE - 90) + TIME '10:00'), NULL, 'completado', CURRENT_DATE - 90, 'Limpieza profunda', 800),
(pg_temp.pac('TOMM931205MDFRRN06'), pg_temp.proc('Ortodoncia (mensual)'), pg_temp.cita('TOMM931205MDFRRN06', (CURRENT_DATE - 15) + TIME '09:00'), NULL, 'completado', CURRENT_DATE - 15, 'Ajuste mensual', 1800),
-- En proceso: no debe poder pagarse hasta completarse (RN02, TC-81)
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.proc('Endodoncia'),           NULL, 30, 'en_proceso', CURRENT_DATE - 5, 'Endodoncia en dos sesiones', 3000),
-- Pendiente: ligada a la cita futura de obturación
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.proc('Obturación (resina)'),  pg_temp.cita('LOMG900520MDFPRB03', (CURRENT_DATE + 7) + TIME '10:00'), 3, 'pendiente', NULL, 'Obturación programada', 1200);

-- ---------------------------------------------------------------------
-- Pagos
-- ---------------------------------------------------------------------
INSERT INTO pagos (paciente_id, procedimiento_id, monto, metodo_pago, fecha_pago, concepto, notas) VALUES
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.pp('MERR850315HDFNMB09', 'Consulta inicial'),     500,  'efectivo',        CURRENT_DATE - 60, 'Consulta inicial', 'Pago completo'),
(pg_temp.pac('MERR850315HDFNMB09'), pg_temp.pp('MERR850315HDFNMB09', 'Limpieza dental'),      800,  'tarjeta_debito',  CURRENT_DATE - 45, 'Limpieza dental', 'Pago completo'),
(pg_temp.pac('LOMG900520MDFPRB03'), pg_temp.pp('LOMG900520MDFPRB03', 'Consulta inicial'),     500,  'transferencia',   CURRENT_DATE - 40, 'Consulta inicial', NULL),
(pg_temp.pac('SACP780810HDFNRD08'), pg_temp.pp('SACP780810HDFNRD08', 'Obturación (resina)'),  500,  'efectivo',        CURRENT_DATE - 30, 'Anticipo obturación', 'Pago parcial'),
(pg_temp.pac('RUMA970304MDFBND08'), pg_temp.pp('RUMA970304MDFBND08', 'Endodoncia'),           1500, 'tarjeta_credito', CURRENT_DATE - 20, 'Anticipo endodoncia', 'Pago parcial'),
(pg_temp.pac('GAPE870918HDFRRD05'), pg_temp.pp('GAPE870918HDFRRD05', 'Limpieza dental'),      800,  'efectivo',        CURRENT_DATE - 90, 'Limpieza dental', 'Pago completo'),
(pg_temp.pac('TOMM931205MDFRRN06'), pg_temp.pp('TOMM931205MDFRRN06', 'Ortodoncia (mensual)'), 1000, 'transferencia',   CURRENT_DATE - 15, 'Mensualidad ortodoncia', 'Pago parcial');

-- ---------------------------------------------------------------------
-- Odontogramas (numeración universal 1-32)
-- ---------------------------------------------------------------------
INSERT INTO estados_dentales (paciente_id, diente_numero, estado, notas) VALUES
(pg_temp.pac('SACP780810HDFNRD08'), 14, 'obturado',       'Obturación con resina'),
(pg_temp.pac('SACP780810HDFNRD08'), 15, 'cariado',        'Caries incipiente, vigilar'),
(pg_temp.pac('VASL881112HDFRNS02'), 17, 'extraido',       'Tercer molar extraído'),
(pg_temp.pac('RUMA970304MDFBND08'), 19, 'obturado',       'Endodoncia concluida, pendiente corona'),
(pg_temp.pac('LOMG900520MDFPRB03'), 30, 'en_tratamiento', 'Endodoncia en proceso'),
(pg_temp.pac('LOMG900520MDFPRB03'),  3, 'cariado',        'Obturación programada'),
(pg_temp.pac('TOMM931205MDFRRN06'),  8, 'en_tratamiento', 'Ortodoncia activa'),
(pg_temp.pac('TOMM931205MDFRRN06'),  9, 'en_tratamiento', 'Ortodoncia activa'),
(pg_temp.pac('GAPE870918HDFRRD05'),  2, 'corona',         'Corona de porcelana previa');

-- ---------------------------------------------------------------------
-- Historial médico
-- ---------------------------------------------------------------------
INSERT INTO historial_medico (paciente_id, fecha, tipo, descripcion, observaciones, realizado_por) VALUES
(pg_temp.pac('MERR850315HDFNMB09'), CURRENT_DATE - 60, 'consulta',      'Primera consulta', 'Buena salud bucal general.', pg_temp.med('angel.dominguez@sonrisaperfecta.mx')),
(pg_temp.pac('LOMG900520MDFPRB03'), CURRENT_DATE - 40, 'consulta',      'Consulta inicial, paciente diabética', 'Diabetes controlada.', pg_temp.med('carlos.rodriguez@sonrisaperfecta.mx')),
(pg_temp.pac('SACP780810HDFNRD08'), CURRENT_DATE - 30, 'procedimiento', 'Obturación en diente 14', 'Paciente nervioso pero cooperó.', pg_temp.med('angel.dominguez@sonrisaperfecta.mx')),
(pg_temp.pac('RUMA970304MDFBND08'), CURRENT_DATE - 20, 'procedimiento', 'Endodoncia en diente 19', 'Sin complicaciones.', pg_temp.med('ana.martinez@sonrisaperfecta.mx'));

-- ---------------------------------------------------------------------
-- Cuentas de acceso adicionales (contraseña de ambas: 1234)
-- ---------------------------------------------------------------------
INSERT INTO usuarios_sistema (username, password, nombre, puesto, es_superadmin, permisos, medico_id) VALUES
('alisson', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
 'Alisson Reyes', 'Recepcionista', false,
 '{"menus": ["dashboard", "citas", "pacientes", "expedientes", "adeudos"], "puede_eliminar": false}', NULL),
('Angel', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
 'Dr. Ángel Domínguez Ruiz', 'Médico dentista', false,
 '{"menus": ["dashboard", "citas", "pacientes", "expedientes", "odontograma"], "puede_eliminar": false}',
 pg_temp.med('angel.dominguez@sonrisaperfecta.mx'));

COMMIT;
