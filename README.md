# Contability App

Esta es una aplicación de contabilidad que permite gestionar usuarios, pedidos, productos y tiendas.

## Requisitos

- Python 3.x
- Django
- PostgreSQL (o cualquier otra base de datos compatible con Django)

## Instalación

1. Clona el repositorio:
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd Contability-app
   ```

2. Crea y activa un entorno virtual:
   ```sh
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

4. Configura la base de datos en `settings.py`.

5. Realiza las migraciones:
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Crea un superusuario:
   ```sh
   python manage.py createsuperuser
   ```

7. Ejecuta el servidor de desarrollo:
   ```sh
   python manage.py runserver
   ```
