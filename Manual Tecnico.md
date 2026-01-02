# Manual técnico
Instalación del sistema
- [Requisitos técnicos](#Requisitos-técnicos)
- [Instalación](#Proceso-técnico-de-instalación)
- [Accediendo al sistema](#Accediendo-al-sistema)

## Requisitos técnicos
- Servidor ejecutando Debian 12 o superior
- Usuario con privilegios `sudo`
- Python 3.12 o superior.
- Pip o superiores
- Docker Engine y Docker Compose

## Proceso técnico de instalación
1. Descargue o clone el repositorio de GitHub con:

`git clone https://github.com/yaelrdf/Ingenieria-diseno-UPIICSA`

2. En el directorio donde se realizó la descarga.
3. Ejecute el script de instalación: ````python3 install.py````
4. El instalador buscará dependencias e instalará los requerimientos necesarios.
5. Después de esto el instalador mostrará un mensaje de error en caso de no cumplir con alguno de los requerimientos, el instalador podrá instalarlos.
````
Falta la dependencia: docker
¿Deseas intentar instalar {item}? (Requiere sudo)
````
En caso de no tener éxito instalando el requerimiento se tendrá que instalar manualmente:
````
No se pudo instalar {item}. Por favor instálalo manualmente.

El sistema requiere {item} para continuar.
````
6. En caso de contar con todos los requerimientos el instalador continuará con la instalación en el siguiente orden:
   1. Creación del entorno virtual de Python
   2. Instalación de paquetería necesaria de Python
   3. Creación e inicio del contenedor Docker Postgres con la base de datos
   4. Configuración de la base de datos (Creación de tablas)
   5. Creación de un systemd service para el sistema (__Opcional__)

7. El instalador preguntará si desea configurar un "System Service" para la ejecución automática del sistema
````
¿Deseas crear un servicio de sistema (systemd) para que el sistema inicie automáticamente?
````
> [!WARNING]
> No es posible volver a este paso si se niega, se tendrá que hacer una configuración manual.

8. El instalador creará el archivo de servicio y preguntará si desea instalarlo automáticamente:
````
¿Desea instalar y activar el servicio ahora mismo? (Requiere sudo)
````
Si acepta, el instalador instalará y activará el servicio.

9. Al finalizar, el instalador proporcionará el comando para ejecutar el sistema de forma manual en caso requerido. 
10. El instalador finalizará con un mensaje de éxito. 
````
¡Instalación completada con éxito!
````

## Accediendo al sistema
Después de la instalación el sistema web estará accesible en toda la red local del servidor en el puerto 8080.

Para acceder al sistema ingrese a la dirección `http://ip_servidor:8080` en cualquier equipo conectado a la misma red que el servidor.