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

## API Endpoints

## Autenticación

### Registro de usuario
- **URL:** `/api/register/`
- **Método:** `POST`
- **Descripción:** Registra un nuevo usuario.
- **Cuerpo de la solicitud:**
  ```json
  {
    "email": "user@example.com",
    "name": "John",
    "last_name": "Doe",
    "password": "password123"
  }
  ```

### Inicio de sesión
- **URL:** `/api/login/`
- **Método:** `POST`
- **Descripción:** Inicia sesión un usuario.
- **Cuerpo de la solicitud:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```

## Usuarios

### Obtener detalles del usuario
- **URL:** `/api/user/`
- **Método:** `GET`
- **Descripción:** Obtiene los detalles del usuario autenticado.

### Actualizar detalles del usuario
- **URL:** `/api/user/`
- **Método:** `PUT`
- **Descripción:** Actualiza los detalles del usuario autenticado.
- **Cuerpo de la solicitud:**
  ```json
  {
    "name": "John",
    "last_name": "Doe",
    "home_address": "123 Main St",
    "phone_number": "555-555-5555"
  }
  ```

## Pedidos

### Crear un pedido
- **URL:** `/api/orders/`
- **Método:** `POST`
- **Descripción:** Crea un nuevo pedido.
- **Cuerpo de la solicitud:**
  ```json
  {
    "client_id": 1,
    "sales_manager_id": 2,
    "status": "Pendiente",
    "pay_status": "No pagado"
  }
  ```

### Obtener lista de pedidos
- **URL:** `/api/orders/`
- **Método:** `GET`
- **Descripción:** Obtiene la lista de todos los pedidos.

### Obtener detalles de un pedido
- **URL:** `/api/orders/{id}/`
- **Método:** `GET`
- **Descripción:** Obtiene los detalles de un pedido específico.

### Actualizar un pedido
- **URL:** `/api/orders/{id}/`
- **Método:** `PUT`
- **Descripción:** Actualiza los detalles de un pedido específico.
- **Cuerpo de la solicitud:**
  ```json
  {
    "status": "Completado",
    "pay_status": "Pagado"
  }
  ```

### Eliminar un pedido
- **URL:** `/api/orders/{id}/`
- **Método:** `DELETE`
- **Descripción:** Elimina un pedido específico.

## Productos

### Crear un producto
- **URL:** `/api/products/`
- **Método:** `POST`
- **Descripción:** Crea un nuevo producto.
- **Cuerpo de la solicitud:**
  ```json
  {
    "sku": "12345",
    "name": "Producto A",
    "shop_id": 1,
    "amount_requested": 10,
    "shop_cost": 100.0
  }
  ```

### Obtener lista de productos
- **URL:** `/api/products/`
- **Método:** `GET`
- **Descripción:** Obtiene la lista de todos los productos.

### Obtener detalles de un producto
- **URL:** `/api/products/{id}/`
- **Método:** `GET`
- **Descripción:** Obtiene los detalles de un producto específico.

### Actualizar un producto
- **URL:** `/api/products/{id}/`
- **Método:** `PUT`
- **Descripción:** Actualiza los detalles de un producto específico.
- **Cuerpo de la solicitud:**
  ```json
  {
    "name": "Producto B",
    "amount_requested": 20,
    "shop_cost": 150.0
  }
  ```

### Eliminar un producto
- **URL:** `/api/products/{id}/`
- **Método:** `DELETE`
- **Descripción:** Elimina un producto específico.

## Tiendas

### Crear una tienda
- **URL:** `/api/shops/`
- **Método:** `POST`
- **Descripción:** Crea una nueva tienda.
- **Cuerpo de la solicitud:**
  ```json
  {
    "name": "Tienda A",
    "link": "https://example.com"
  }
  ```

### Obtener lista de tiendas
- **URL:** `/api/shops/`
- **Método:** `GET`
- **Descripción:** Obtiene la lista de todas las tiendas.

### Obtener detalles de una tienda
- **URL:** `/api/shops/{id}/`
- **Método:** `GET`
- **Descripción:** Obtiene los detalles de una tienda específica.

### Actualizar una tienda
- **URL:** `/api/shops/{id}/`
- **Método:** `PUT`
- **Descripción:** Actualiza los detalles de una tienda específica.
- **Cuerpo de la solicitud:**
  ```json
  {
    "name": "Tienda B",
    "link": "https://example.com"
  }
  ```

### Eliminar una tienda
- **URL:** `/api/shops/{id}/`
- **Método:** `DELETE`
- **Descripción:** Elimina una tienda específica.