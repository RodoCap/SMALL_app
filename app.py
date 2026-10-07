from flask import Flask, request, jsonify
from models import Producto, Inventario, Venta

app = Flask(__name__)
inventario = Inventario()

@app.route("/productos", methods=["GET"])
def obtener_productos():
    lista = []
    for p in inventario.productos:
        lista.append({
            "id": p.id_producto,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "compra": p.compra,
            "venta": p.venta,
            "stock_actual": p.stock_actual
        })
    return jsonify(lista)

@app.route("/productos", methods=["POST"])
def crear_producto():
    datos = request.get_json()
    nuevo = Producto(
        nombre=datos["nombre"],
        compra=datos["compra"],
        venta=datos["venta"],
        cantidad_comprada=datos["cantidad_comprada"],
        id_producto=datos["id_producto"],
        categoria=datos["categoria"]
    )
    inventario.agregar_producto(nuevo)
    return jsonify({"mensaje": "Producto creado"}), 201

@app.route("/productos/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    eliminado = inventario.eliminar_producto(id_producto)
    if eliminado:
        return jsonify({"mensaje": "Producto eliminado"}), 200
    return jsonify({"mensaje": "Producto no encontrado"}), 404

@app.route("/ventas", methods=["POST"])
def crear_venta():
    datos = request.get_json()
    try:
        resultado = inventario.registrar_venta(
            id_producto=datos["id_producto"],
            cantidad=datos["cantidad"]
        )
        if resultado:
            return jsonify({"mensaje": "Venta registrada"}), 201
        return jsonify({"mensaje": "Producto no encontrado"}), 404
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400

@app.route("/resumen", methods=["GET"])
def obtener_resumen():
    total_invertido = sum(p.total_invertido for p in inventario.productos)
    ganancia_total = sum(p.ganancia for p in inventario.productos)
    total_vendido = sum(v.total for v in inventario.ventas)

    return jsonify({
        "total_invertido": total_invertido,
        "total_vendido": total_vendido,
        "ganancia_total": ganancia_total
    })

if __name__ == "__main__":
    app.run(debug=True)



