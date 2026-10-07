import sqlite3
from models import Producto,Venta


def conectar():
    conexion = sqlite3.connect("inventario.db")
    conexion.row_factory = sqlite3.Row
    return conexion

def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT,
            compra REAL NOT NULL,
            venta REAL NOT NULL,
            cantidad_comprada INTEGER NOT NULL,
            cantidad_vendida INTEGER NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

def crear_tabla_ventas(): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad_vendida INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            costo_unitario REAL NOT NULL 
        )
    """)
    conexion.commit()
    conexion.close()

def insertar_producto(producto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO productos (id_producto, nombre, categoria, compra, venta, cantidad_comprada, cantidad_vendida)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (producto.id_producto, producto.nombre, producto.categoria, producto.compra, producto.venta, producto.cantidad_comprada, producto.cantidad_vendida))
    conexion.commit()
    conexion.close()



def insertar_venta(venta): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO ventas (fecha, producto, cantidad_vendida, precio_unitario, costo_unitario)
        VALUES (?, ?, ?, ?, ?)
    """, (venta.fecha, venta.producto, venta.cantidad_vendida, venta.precio_unitario, venta.costo_unitario))    
    conexion.commit()
    conexion.close()    

def obtener_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    filas = cursor.fetchall()
    conexion.close()

    productos = []
    for fila in filas:
        p = Producto(
            nombre=fila["nombre"],
            compra=fila["compra"],
            venta=fila["venta"],
            cantidad_comprada=fila["cantidad_comprada"],
            id_producto=fila["id_producto"],
            categoria=fila["categoria"]
        )
        p.cantidad_vendida = fila["cantidad_vendida"]
        productos.append(p)
    return productos

def obtener_ventas(): 
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ventas")
    filas = cursor.fetchall()
    conexion.close()

    ventas = []
    for fila in filas: 
        v = Venta(
            fecha = fila["fecha"],
            producto = fila["producto"],
            cantidad_vendida = fila["cantidad_vendida"],
            precio_unitario = fila["precio_unitario"],
            costo_unitario = fila["costo_unitario"]
        )
        ventas.append(v)
    return ventas

def eliminar_producto(id_producto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
    conexion.commit()
    conexion.close()

def actualizar_producto(producto):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE productos SET cantidad_vendida = ? WHERE id_producto = ?
    """, (producto.cantidad_vendida, producto.id_producto))
    conexion.commit()
    conexion.close()