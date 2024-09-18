# Manual de arranque de proyecto

## Requisitos previos:

### LINUX / MAC

Para ejecutar el proyecto en Linux, Mac o Windows, es importante cumplir con algunos requisitos previos.
Se requiere de mínimo 4GB de RAM y 15GB de espacio en almacenamiento.
En el caso de Linux/Mac, primero debes tener Python 3.x instalado. 
Puedes verificar si está disponible ejecutando 

### `python3 --version`

y si no lo tienes, lo puedes instalar usando el gestor de paquetes de tu sistema. 
En Ubuntu o Debian, ejecuta 

### `sudo apt-get install python3 python3-pip`

mientras que en macOS puedes instalarlo usando

### `brew install python3`

También necesitas pip, el gestor de paquetes de Python, que generalmente viene con Python 3, 
pero puedes asegurarte de tener la última versión ejecutando.

### `python3 -m pip install --upgrade pip`

Otro requisito es Node.js y npm, que son necesarios para gestionar las dependencias del cliente. 
En Ubuntu/Debian los puedes instalar con 

### `sudo apt-get install nodejs npm`

y en macOS con 

### `brew install node` 

### WINDOWS

En el caso de Windows, también necesitas Python 3.x. 
Para verificar si está instalado, puedes ejecutar 

### `python --version`

y si no lo tienes, debes descargarlo e instalarlo desde [python.org](python.org), 
asegurándote de marcar la opción "Add Python to PATH" durante la instalación. 
Luego, verifica que pip esté actualizado con 

### `python -m pip install --upgrade pip`

Para Node.js y npm, puedes descargarlos desde [nodejs.org](nodejs.org), 
y una vez instalados, puedes verificar que estén funcionando correctamente ejecutando.

### `node --version y npm --version`

Además de estos requisitos, en ambos sistemas operativos necesitarás tener Git instalado para clonar el repositorio. 
En Linux puedes instalarlo con 

### `sudo apt-get install git`

y en macOS con 

### `brew install git`

En Windows, puedes descargarlo e instalarlo desde [git-scm.com](git-scm.com).

## Instrucciones para ejecutar en local:

Clonar el repositorio y ejecutar los siguientes comandos:

### `python3 -m venv myenv`(Linux/Mac) o `python -m -venv myenv`(Windows)

Se crea un entorno virtual para instalar y ejecutar las dependencias y la aplicación web.

### `source myenv/bin/activate` o `.\myenv\Scripts\Activate`

Se activa el entorno virtual (Linux/Mac o Windows, respectivamente).

### `pip install -r requirements.txt`

Se instalan las todas las dependencias. Habrá que esperar unos minutos.

### `python3 -m spacy download es_core_news_sm`(Linux/Mac) 
### o `python -m spacy download es_core_news_sm`(Windows)

Se instala el modelo de spaCy.

### `cd client`

Se accede a la carpeta de cliente.

### `npm install` y `npm run build`

Se instalan las dependencias y se ejecuta el script de construcción del cliente

### `cd ..`

Se accede de nuevo al inicio.

### `python3 app.py`(Linux/Mac) o `python app.py`(Windows)

Se ejecuta el servidor para que esté disponible.
Abrir [http://127.0.0.1:5001](http://127.0.0.1:5001) en el navegador para probar la aplicación en la web.