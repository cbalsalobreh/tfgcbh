# Manual de arranque de proyecto

Clonar el repositorio y ejecutar los siguientes comandos:

### `python3 -m venv venv`

Se crea un entorno virtual para instalar las dependencias.

### `source venv/bin/activate`

Se activa el entorno virtual.

### `python3.9 -m pip install requirements.txt`

Se instalan las todas las dependencias.

### `python -m spacy download es_core_news_sm`

Se instala el modelo de spaCy.

### `python3 app.py`

Se ejecuta el servidor para que esté disponible.

Abrir [http://127.0.0.1:5001](http://127.0.0.1:5001) en el navegador para probar la aplicación en la web.