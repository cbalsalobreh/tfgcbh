# Manual de arranque de proyecto

Clonar el repositorio y ejecutar los siguientes comandos:

### `pip3 install -r requirements.txt`

Se instalan las todas las dependencias.

### `python3 -m spacy download es_core_news_sm`

Se instala el modelo de spaCy.

### `cd client`

Se accede a la carpeta de cliente.

### `npm install` y `npm run build`

Se instalan las dependencias y se ejecutan el script de construcción del cliente

### `cd ..`

Se accede de nuevo al inicio.

### `python3 app.py`

Se ejecuta el servidor para que esté disponible.

Abrir [http://127.0.0.1:5001](http://127.0.0.1:5001) en el navegador para probar la aplicación en la web.