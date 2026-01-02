import os
import subprocess
import sys
import shutil
import time
import getpass

def check_dependency(command):
    """Revisa si un comando está disponible en el sistema."""
    return shutil.which(command) is not None

def check_docker_compose():
    """Revisa si docker compose (V2) está disponible."""
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def ask_user(question):
    """Pregunta al usuario y retorna True si la respuesta es 's' o 'y'."""
    response = input(f"{question} (s/n): ").lower()
    return response in ['s', 'y', 'si', 'yes']

def install_dependency(pkg):
    """Intenta instalar dependencias básicas (asumiendo Debian/Ubuntu)."""
    print(f"Intentando instalar {pkg}...")
    try:
        if pkg == 'pip':
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-pip'], check=True)
        elif pkg == 'docker':
            subprocess.run(['curl', '-fsSL', 'https://get.docker.com', '-o', 'get-docker.sh'], check=True)
            subprocess.run(['sudo', 'sh', 'get-docker.sh'], check=True)
            if os.path.exists('get-docker.sh'):
                os.remove('get-docker.sh')
        elif pkg == 'docker compose':
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'docker-compose-plugin'], check=True)
        print(f"{pkg} instalado correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar {pkg}: {e}")
        return False

def main():
    print("=== Instalador del sistema dental ===")
    
    # 1. Revisar dependencias
    dependencies = {
        'pip': 'pip3',
        'docker': 'docker',
    }
    
    missing = []
    for name, cmd in dependencies.items():
        if not check_dependency(cmd):
            missing.append(name)
    
    if not check_docker_compose():
        missing.append('docker compose')
        
    for item in missing:
        print(f"[!] Falta la dependencia: {item}")
        if ask_user(f"¿Deseas intentar instalar {item}? (Requiere sudo)"):
            if not install_dependency(item):
                print(f"No se pudo instalar {item}. Por favor instálalo manualmente.")
                sys.exit(1)
        else:
            print(f"El sistema requiere {item} para continuar.")
            sys.exit(1)

    # 2. Crear entorno virtual
    print("\n--- Creando entorno virtual ---")
    venv_dir = os.path.join(os.getcwd(), ".venv")
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("Entorno virtual creado en .venv")
    else:
        print("El entorno virtual ya existe.")

    # 3. Instalar requerimientos
    print("\n--- Instalando requerimientos de Python ---")
    pip_path = os.path.join(venv_dir, "bin", "pip")
    if not os.path.exists(pip_path): # Windows support
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
        
    requirements_path = os.path.join("Sistema", "requirements.txt")
    if os.path.exists(requirements_path):
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", requirements_path], check=True)
        print("Requerimientos instalados.")
        
        # Actualizar requirements.txt
        print("Actualizando requirements.txt...")
        with open(requirements_path, "w") as f:
            subprocess.run([pip_path, "freeze"], stdout=f, check=True)
    else:
        print(f"Advertencia: No se encontró {requirements_path}")

    # 4. Iniciar contenedor Docker
    print("\n--- Iniciando base de datos (Docker) ---")
    if os.path.exists("compose.yml"):
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        print("Contenedores iniciados.")
    else:
        print("Error: No se encontró compose.yml")
        sys.exit(1)

    # 5. Ejecutar script SQL
    print("\n--- Configurando base de datos ---")
    sql_script = os.path.join("Sistema", "create_database.sql")
    if os.path.exists(sql_script):
        print("Esperando a que la base de datos esté lista...")
        # Intentar esperar a que el contenedor esté listo
        max_retries = 30
        connected = False
        for i in range(max_retries):
            try:
                # Intentamos correr un comando simple
                result = subprocess.run([
                    "docker", "compose", "exec", "-T", "db", 
                    "pg_isready", "-U", "postgres"
                ], capture_output=True)
                if result.returncode == 0:
                    connected = True
                    break
            except:
                pass
            time.sleep(2)
        
        if connected:
            print("Ejecutando script SQL...")
            # Usamos -T para evitar errores de TTY en algunos entornos
            with open(sql_script, "r") as f:
                # Nota: create_database.sql intenta crear la DB, pero compose ya la creó.
                # Corremos contra la db 'postgres' para que el script pueda crear 'sistema_dental' y conectarse.
                # No usamos check=True aquí porque el CREATE DATABASE puede fallar si ya existe.
                process = subprocess.run([
                    "docker", "compose", "exec", "-T", "db", 
                    "psql", "-U", "postgres"
                ], stdin=f, capture_output=True, text=True)
                
                if process.returncode != 0:
                    if "already exists" in process.stderr:
                        print("La base de datos ya existe, continuando con la creación de tablas...")
                    else:
                        print(f"Error al ejecutar SQL: {process.stderr}")
                else:
                    print("Base de datos configurada correctamente.")
        else:
            print("Error: No se pudo conectar a la base de datos después de varios intentos.")
    else:
        print(f"Advertencia: No se encontró {sql_script}")

    # 6. Preguntar por servicio de sistema
    print("\n--- Configuración de servicio de sistema ---")
    if ask_user("¿Desea crear un servicio de sistema (systemd) para que el sistema inicie automáticamente?"):
        user = getpass.getuser()
        current_dir = os.getcwd()
        python_executable = os.path.join(venv_dir, "bin", "python")
        
        service_content = f"""[Unit]
Description=Sistema Dental
After=network.target docker.service

[Service]
Type=simple
User={user}
WorkingDirectory={current_dir}
ExecStart={python_executable} Sistema/main.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
        service_file = "sistema_dental.service"
        try:
            with open(service_file, "w") as f:
                f.write(service_content)
            
            print(f"\nArchivo de servicio creado: {service_file}")
            
            if ask_user("¿Desea instalar y activar el servicio ahora mismo? (Requiere sudo)"):
                try:
                    print("Instalando servicio...")
                    subprocess.run(["sudo", "mv", service_file, "/etc/systemd/system/"], check=True)
                    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
                    subprocess.run(["sudo", "systemctl", "enable", "sistema_dental"], check=True)
                    subprocess.run(["sudo", "systemctl", "start", "sistema_dental"], check=True)
                    print("Servicio instalado, habilitado e iniciado correctamente.")
                except subprocess.CalledProcessError as e:
                    print(f"Error al instalar el servicio: {e}")
                    print("Puede intentar instalarlo manualmente con los siguientes comandos:")
                    print(f"  sudo mv {service_file} /etc/systemd/system/")
                    print("  sudo systemctl daemon-reload")
                    print("  sudo systemctl enable sistema_dental")
                    print("  sudo systemctl start sistema_dental")
            else:
                print("Para instalarlo manualmente, ejecuta los siguientes comandos:")
                print(f"  sudo mv {service_file} /etc/systemd/system/")
                print("  sudo systemctl daemon-reload")
                print("  sudo systemctl enable sistema_dental")
                print("  sudo systemctl start sistema_dental")
        except Exception as e:
            print(f"Error al crear el archivo de servicio: {e}")
    
    # 7. Finalizar
    print("\n" + "="*40)
    print("¡Instalación completada con éxito!")
    print("Para iniciar el sistema manualmente, usa:")
    if os.name == 'nt':
        print(f"  {os.path.join('.venv', 'Scripts', 'activate')} && python Sistema/main.py")
    else:
        print(f"  source .venv/bin/activate && python Sistema/main.py")
    print("="*40)

if __name__ == "__main__":
    main()
