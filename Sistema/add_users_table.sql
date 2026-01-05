-- Add costo column to citas if it doesn't exist (it's used in the code but missing in initial SQL)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='citas' AND column_name='costo') THEN
        ALTER TABLE citas ADD COLUMN costo DECIMAL(10,2) DEFAULT 0;
    END IF;
END $$;

-- SQL script to add system users table
CREATE TABLE IF NOT EXISTS usuarios_sistema (
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

-- Default admin user (password: admin123)
-- Hash: 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
INSERT INTO usuarios_sistema (username, password, nombre, puesto, es_superadmin, permisos)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Administrador', 'Super Usuario', true, '{"menus": ["dashboard", "citas", "pacientes", "expedientes", "odontograma", "adeudos", "medicos", "usuarios"], "puede_eliminar": true}')
ON CONFLICT (username) DO NOTHING;
