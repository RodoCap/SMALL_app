# Sistema de Inventario — SMALL_app

API REST para gestionar el inventario y ventas de un negocio de accesorios tecnológicos (cables, audífonos, adaptadores, power banks).

## Tecnologías
- Python
- Flask
- SQLite

## Estructura del proyecto
- `models.py` — Clases Producto, Inventario y Venta (POO, validaciones, propiedades calculadas)
- `database.py` — Conexión y operaciones con SQLite
- `app.py` — Rutas de la API (Flask)

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | /productos | Lista todos los productos |
| POST | /productos | Crea un producto nuevo |
| DELETE | /productos/<id> | Elimina un producto |
| POST | /ventas | Registra una venta (descuenta stock) |
| GET | /resumen | Totales: invertido, vendido, ganancia |

## Cómo correrlo

\`\`\`
python -m venv venv
venv\\Scripts\\activate
pip install flask
python app.py
\`\`\`

El servidor corre en `http://127.0.0.1:5000`

## Estado actual
Backend funcional con persistencia en SQLite (Fase 1 completa). Próxima fase: interfaz web/móvil.