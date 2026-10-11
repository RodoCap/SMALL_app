import os
from flask import Flask, request, jsonify, send_from_directory
from models import Producto, Inventario
import database

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # fotos de hasta 8 MB

CARPETA_FOTOS = os.path.join(app.static_folder, "fotos")
os.makedirs(CARPETA_FOTOS, exist_ok=True)

inventario = Inventario()

database.crear_tabla()
database.crear_tabla_ventas()
inventario.productos = database.obtener_productos()
inventario.ventas = database.obtener_ventas()


# ---------- Ayudas ----------
def ruta_foto(id_producto):
    return os.path.join(CARPETA_FOTOS, f"{id_producto}.jpg")

def url_foto(id_producto):
    ruta = ruta_foto(id_producto)
    if os.path.exists(ruta):
        # ?v=... obliga al navegador a mostrar la foto nueva si la reemplazas
        return f"/static/fotos/{id_producto}.jpg?v={int(os.path.getmtime(ruta))}"
    return None

def producto_a_dict(p):
    return {
        "id": p.id_producto,
        "nombre": p.nombre,
        "categoria": p.categoria,
        "compra": p.compra,
        "venta": p.venta,
        "cantidad_comprada": p.cantidad_comprada,
        "cantidad_vendida": p.cantidad_vendida,
        "stock_actual": p.stock_actual,
        "total_invertido": p.total_invertido,
        "total_vendido": p.total_vendido,
        "ganancia": p.ganancia,
        "ganancia_unitaria": p.ganancia_unitaria,
        "foto": url_foto(p.id_producto)
    }

def error(mensaje, codigo):
    return jsonify({"mensaje": mensaje}), codigo


@app.errorhandler(413)
def foto_muy_pesada(e):
    return error("La foto pesa demasiado (máximo 8 MB)", 413)


# ---------- Página ----------
@app.route("/")
def inicio():
    return send_from_directory("static", "index.html")


# ---------- Productos ----------
@app.route("/productos", methods=["GET"])
def obtener_productos():
    return jsonify([producto_a_dict(p) for p in inventario.productos])

@app.route("/productos", methods=["POST"])
def crear_producto():
    datos = request.get_json(silent=True) or {}
    try:
        if inventario.buscar_producto(datos["id_producto"]):
            return error("Ya existe un producto con ese ID", 409)
        nuevo = Producto(
            nombre=datos["nombre"],
            compra=datos["compra"],
            venta=datos["venta"],
            cantidad_comprada=datos["cantidad_comprada"],
            id_producto=datos["id_producto"],
            categoria=datos["categoria"]
        )
    except KeyError as falta:
        return error(f"Falta el dato {falta}", 400)
    except ValueError as problema:
        return error(str(problema), 400)
    except TypeError:
        return error("Hay un dato con formato inválido", 400)
    inventario.agregar_producto(nuevo)
    database.insertar_producto(nuevo)
    return jsonify({"mensaje": "Producto creado"}), 201

@app.route("/productos/<int:id_producto>", methods=["PUT"])
def editar_producto(id_producto):
    producto = inventario.buscar_producto(id_producto)
    if producto is None:
        return error("Producto no encontrado", 404)
    datos = request.get_json(silent=True) or {}
    try:
        producto.actualizar(
            nombre=datos["nombre"],
            categoria=datos["categoria"],
            compra=datos["compra"],
            venta=datos["venta"]
        )
    except KeyError as falta:
        return error(f"Falta el dato {falta}", 400)
    except ValueError as problema:
        return error(str(problema), 400)
    except TypeError:
        return error("Hay un dato con formato inválido", 400)
    database.guardar_producto(producto)
    return jsonify({"mensaje": "Producto actualizado"}), 200

@app.route("/productos/<int:id_producto>/reponer", methods=["POST"])
def reponer_producto(id_producto):
    producto = inventario.buscar_producto(id_producto)
    if producto is None:
        return error("Producto no encontrado", 404)
    datos = request.get_json(silent=True) or {}
    try:
        producto.reponer(datos["cantidad"])
    except KeyError:
        return error("Falta la cantidad", 400)
    except ValueError as problema:
        return error(str(problema), 400)
    database.guardar_producto(producto)
    return jsonify({"mensaje": "Stock repuesto", "stock_actual": producto.stock_actual}), 200

@app.route("/productos/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    eliminado = inventario.eliminar_producto(id_producto)
    if eliminado:
        database.eliminar_producto(id_producto)
        # Borra también su foto: si luego se reutiliza el ID, no hereda la foto vieja
        if os.path.exists(ruta_foto(id_producto)):
            os.remove(ruta_foto(id_producto))
        return jsonify({"mensaje": "Producto eliminado"}), 200
    return error("Producto no encontrado", 404)


# ---------- Foto del producto ----------
@app.route("/productos/<int:id_producto>/foto", methods=["POST"])
def subir_foto(id_producto):
    if inventario.buscar_producto(id_producto) is None:
        return error("Producto no encontrado", 404)
    archivo = request.files.get("foto")
    if archivo is None:
        return error("No llegó ninguna foto", 400)
    contenido = archivo.read()
    if not contenido.startswith(b"\xff\xd8\xff"):  # firma de un archivo JPG
        return error("La foto debe ser un JPG", 400)
    with open(ruta_foto(id_producto), "wb") as f:
        f.write(contenido)
    return jsonify({"mensaje": "Foto guardada", "foto": url_foto(id_producto)}), 200


# ---------- Ventas ----------
@app.route("/ventas", methods=["GET"])
def obtener_ventas():
    return jsonify([
        {
            "fecha": v.fecha,
            "producto": v.producto,
            "cantidad": v.cantidad_vendida,
            "precio_unitario": v.precio_unitario,
            "total": v.total,
            "ganancia": v.ganancia
        }
        for v in inventario.ventas
    ])

@app.route("/ventas", methods=["POST"])
def crear_venta():
    datos = request.get_json(silent=True) or {}
    try:
        producto = inventario.buscar_producto(datos["id_producto"])
        resultado = inventario.registrar_venta(
            id_producto=datos["id_producto"],
            cantidad=datos["cantidad"]
        )
        if resultado:
            ultima_venta = inventario.ventas[-1]
            database.insertar_venta(ultima_venta)
            database.actualizar_producto(producto)
            return jsonify({"mensaje": "Venta registrada"}), 201
        return error("Producto no encontrado", 404)
    except KeyError as falta:
        return error(f"Falta el dato {falta}", 400)
    except ValueError as problema:
        return error(str(problema), 400)
    except TypeError:
        return error("Hay un dato con formato inválido", 400)


# ---------- Resumen ----------
@app.route("/resumen", methods=["GET"])
def obtener_resumen():
    total_invertido = sum(p.total_invertido for p in inventario.productos)
    total_vendido = sum(v.total for v in inventario.ventas)
    # La ganancia sale de las ventas (guardan el precio y costo de ese día)
    ganancia_total = sum(v.ganancia for v in inventario.ventas)

    return jsonify({
        "total_invertido": total_invertido,
        "total_vendido": total_vendido,
        "ganancia_total": ganancia_total
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

