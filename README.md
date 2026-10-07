# 愛 SMALL_app

API de inventario y ventas para mi negocio de accesorios tecnológicos (cables, audífonos, adaptadores y power banks).

Empezó como un Excel y terminó siendo una app propia: registra productos, descuenta stock en cada venta y calcula cuánto he invertido y cuánto he ganado.

##  Qué hace

- Registra productos con costo de compra, precio de venta y cantidad
- Calcula el **stock actual** automáticamente
- Registra ventas y bloquea las que superan el stock disponible
- Muestra un resumen: **total invertido, total vendido y ganancia**
- Guarda todo en SQLite, así los datos no se pierden al cerrar el servidor

## 使用 Hecho con

Python · Flask · SQLite · Programación Orientada a Objetos
S
##  Cómo está organizado

```
app.py        → rutas de la API (recibe y responde peticiones)
models.py     → clases Producto, Inventario y Venta, con sus reglas y cálculos
database.py   → todo lo que habla con SQLite
```

Cada archivo hace una sola cosa: las rutas no tienen SQL y las clases no saben nada de HTTP.

## 工程 Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/productos` | Lista el inventario con su stock |
| POST | `/productos` | Crea un producto |
| DELETE | `/productos/<id>` | Elimina un producto |
| POST | `/ventas` | Registra una venta y descuenta stock |
| GET | `/resumen` | Invertido, vendido y ganancia total |

Ejemplo de venta:

```json
POST /ventas
{ "id_producto": 1, "cantidad": 2 }
```

Si no hay suficiente stock, la API responde con un error `400` y un mensaje claro.

##  Cómo correrlo

```bash
git clone https://github.com/RodoCap/SMALL_app.git
cd SMALL_app
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Queda corriendo en `http://127.0.0.1:5000`. Puedes probarlo con Thunder Client o Postman.

## 🗺️ Lo que sigue

- [ ] Interfaz con pantallas y botones para usarla desde el celular
- [ ] Fecha automática en las ventas
- [ ] Reponer stock y editar productos
- [ ] Resumen por períodos (semana, mes)

---

Hecho por **Rodolfo** · [@RodoCap](https://github.com/RodoCap)
