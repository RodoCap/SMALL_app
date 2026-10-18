import os
import sqlite3
from datetime import date
from models import Producto, Venta, Credito, Abono

# La base y los respaldos viven junto a este archivo, sin importar desde dónde
# se ejecute el programa (así nunca se crea una base vacía por error)
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(CARPETA, "inventario.db")
CARPETA_RESPALDOS = os.path.join(CARPETA, "respaldos")


def conectar():
    conexion = sqlite3.connect(RUTA_DB, timeout=10)  # espera hasta 10 s si la base está ocupada
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
    crear_tabla()
    # la migración de abajo necesita que exista la tabla productos
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER,
            fecha TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad_vendida INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            costo_unitario REAL NOT NULL
        )
    """)
    # Migración: si la base es vieja (sin id_producto), agrega la columna y
    # enlaza las ventas antiguas con su producto por el nombre
    cursor.execute("PRAGMA table_info(ventas)")
    columnas = [fila["name"] for fila in cursor.fetchall()]
    if "id_producto" not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN id_producto INTEGER")
        cursor.execute("""
            UPDATE ventas
            SET id_producto = (SELECT p.id_producto FROM productos p WHERE p.nombre = ventas.producto)
            WHERE id_producto IS NULL
        """)
    conexion.commit()
    conexion.close()

def crear_tablas_creditos():
    crear_tabla_ventas()  # necesita productos y ventas
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creditos (
            id_credito INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            fecha_proximo_pago TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonos (
            id_abono INTEGER PRIMARY KEY AUTOINCREMENT,
            id_credito INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL
        )
    """)
    # Migración: las ventas de un crédito apuntan a su crédito
    cursor.execute("PRAGMA table_info(ventas)")
    columnas = [fila["name"] for fila in cursor.fetchall()]
    if "id_credito" not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN id_credito INTEGER")
    conexion.commit()
    conexion.close()

# ---------- Productos ----------
def insertar_producto(producto):
    conexion = conectar()
    try:
        with conexion:
            conexion.execute("""
                INSERT INTO productos (id_producto, nombre, categoria, compra, venta, cantidad_comprada, cantidad_vendida)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (producto.id_producto, producto.nombre, producto.categoria, producto.compra,
                  producto.venta, producto.cantidad_comprada, producto.cantidad_vendida))
    finally:
        conexion.close()

def obtener_productos():
    conexion = conectar()
    try:
        filas = conexion.execute("SELECT * FROM productos").fetchall()
    finally:
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

def eliminar_producto(id_producto):
    conexion = conectar()
    try:
        with conexion:
            conexion.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
    finally:
        conexion.close()

def actualizar_producto(producto):
    conexion = conectar()
    try:
        with conexion:
            conexion.execute(
                "UPDATE productos SET cantidad_vendida = ? WHERE id_producto = ?",
                (producto.cantidad_vendida, producto.id_producto))
    finally:
        conexion.close()

def guardar_producto(producto):
    # Guarda TODOS los datos editables del producto (para editar y reponer)
    conexion = conectar()
    try:
        with conexion:
            conexion.execute("""
                UPDATE productos
                SET nombre = ?, categoria = ?, compra = ?, venta = ?, cantidad_comprada = ?
                WHERE id_producto = ?
            """, (producto.nombre, producto.categoria, producto.compra, producto.venta,
                  producto.cantidad_comprada, producto.id_producto))
    finally:
        conexion.close()

# ---------- Ventas ----------
def insertar_venta(venta):
    conexion = conectar()
    try:
        with conexion:
            conexion.execute("""
                INSERT INTO ventas (id_producto, fecha, producto, cantidad_vendida, precio_unitario, costo_unitario)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (venta.id_producto, venta.fecha, venta.producto, venta.cantidad_vendida,
                  venta.precio_unitario, venta.costo_unitario))
    finally:
        conexion.close()

def obtener_ventas():
    conexion = conectar()
    try:
        filas = conexion.execute("SELECT * FROM ventas").fetchall()
    finally:
        conexion.close()

    ventas = []
    for fila in filas:
        v = Venta(
            fecha=fila["fecha"],
            producto=fila["producto"],
            cantidad_vendida=fila["cantidad_vendida"],
            precio_unitario=fila["precio_unitario"],
            costo_unitario=fila["costo_unitario"],
            id_producto=fila["id_producto"],
            id_venta=fila["id_venta"],
            id_credito=fila["id_credito"]
        )
        ventas.append(v)
    return ventas

def guardar_venta(venta, producto):
    # Guarda la venta y el stock vendido juntos: o se guardan las dos cosas o ninguna
    conexion = conectar()
    try:
        with conexion:  # confirma si todo sale bien, deshace todo si algo falla
            cursor = conexion.execute("""
                INSERT INTO ventas (id_producto, fecha, producto, cantidad_vendida, precio_unitario, costo_unitario)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (venta.id_producto, venta.fecha, venta.producto, venta.cantidad_vendida,
                  venta.precio_unitario, venta.costo_unitario))
            venta.id_venta = cursor.lastrowid
            conexion.execute(
                "UPDATE productos SET cantidad_vendida = ? WHERE id_producto = ?",
                (producto.cantidad_vendida, producto.id_producto))
    finally:
        conexion.close()

def anular_venta(id_venta, id_producto, cantidad):
    # Borra la venta y devuelve sus unidades al stock, todo en una sola transacción
    conexion = conectar()
    try:
        with conexion:
            conexion.execute("DELETE FROM ventas WHERE id_venta = ?", (id_venta,))
            if id_producto is not None:
                conexion.execute(
                    "UPDATE productos SET cantidad_vendida = MAX(0, cantidad_vendida - ?) WHERE id_producto = ?",
                    (cantidad, id_producto))
    finally:
        conexion.close()

# ---------- Créditos ----------
def guardar_credito(credito):
    # Guarda el crédito, sus ventas, el stock vendido y el primer abono: todo o nada
    conexion = conectar()
    try:
        with conexion:
            cursor = conexion.execute(
                "INSERT INTO creditos (cliente, fecha, fecha_proximo_pago) VALUES (?, ?, ?)",
                (credito.cliente, credito.fecha, credito.fecha_proximo_pago))
            credito.id_credito = cursor.lastrowid
            for v in credito.ventas:
                v.id_credito = credito.id_credito
                cursor = conexion.execute("""
                    INSERT INTO ventas (id_producto, fecha, producto, cantidad_vendida, precio_unitario, costo_unitario, id_credito)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (v.id_producto, v.fecha, v.producto, v.cantidad_vendida,
                      v.precio_unitario, v.costo_unitario, v.id_credito))
                v.id_venta = cursor.lastrowid
                conexion.execute(
                    "UPDATE productos SET cantidad_vendida = cantidad_vendida + ? WHERE id_producto = ?",
                    (v.cantidad_vendida, v.id_producto))
            for a in credito.abonos:
                a.id_credito = credito.id_credito
                cursor = conexion.execute(
                    "INSERT INTO abonos (id_credito, fecha, monto) VALUES (?, ?, ?)",
                    (a.id_credito, a.fecha, a.monto))
                a.id_abono = cursor.lastrowid
    finally:
        conexion.close()

def guardar_abono(abono):
    conexion = conectar()
    try:
        with conexion:
            cursor = conexion.execute(
                "INSERT INTO abonos (id_credito, fecha, monto) VALUES (?, ?, ?)",
                (abono.id_credito, abono.fecha, abono.monto))
            abono.id_abono = cursor.lastrowid
    finally:
        conexion.close()

def obtener_creditos(ventas):
    # Recibe la lista de ventas ya cargada y se la reparte a cada crédito
    conexion = conectar()
    try:
        filas_creditos = conexion.execute("SELECT * FROM creditos").fetchall()
        filas_abonos = conexion.execute("SELECT * FROM abonos").fetchall()
    finally:
        conexion.close()

    creditos = {}
    for f in filas_creditos:
        creditos[f["id_credito"]] = Credito(
            cliente=f["cliente"], fecha=f["fecha"],
            fecha_proximo_pago=f["fecha_proximo_pago"], id_credito=f["id_credito"])
    for v in ventas:
        if v.id_credito in creditos:
            creditos[v.id_credito].ventas.append(v)
    for f in filas_abonos:
        if f["id_credito"] in creditos:
            creditos[f["id_credito"]].abonos.append(
                Abono(fecha=f["fecha"], monto=f["monto"],
                      id_credito=f["id_credito"], id_abono=f["id_abono"]))
    return list(creditos.values())

def anular_credito(credito):
    # Devuelve el stock y borra ventas, abonos y crédito: todo o nada
    conexion = conectar()
    try:
        with conexion:
            for v in credito.ventas:
                conexion.execute(
                    "UPDATE productos SET cantidad_vendida = MAX(0, cantidad_vendida - ?) WHERE id_producto = ?",
                    (v.cantidad_vendida, v.id_producto))
            conexion.execute("DELETE FROM ventas WHERE id_credito = ?", (credito.id_credito,))
            conexion.execute("DELETE FROM abonos WHERE id_credito = ?", (credito.id_credito,))
            conexion.execute("DELETE FROM creditos WHERE id_credito = ?", (credito.id_credito,))
    finally:
        conexion.close()

# ---------- Respaldo ----------
def hacer_respaldo(guardar_ultimos=14):
    # Copia la base a respaldos/inventario_AAAA-MM-DD.db y conserva solo las más recientes
    if not os.path.exists(RUTA_DB):
        return None
    os.makedirs(CARPETA_RESPALDOS, exist_ok=True)
    destino = os.path.join(CARPETA_RESPALDOS, f"inventario_{date.today().isoformat()}.db")
    origen = sqlite3.connect(RUTA_DB)
    copia = sqlite3.connect(destino)
    try:
        origen.backup(copia)  # copia segura aunque la base esté en uso
    finally:
        copia.close()
        origen.close()
    archivos = sorted(f for f in os.listdir(CARPETA_RESPALDOS)
                      if f.startswith("inventario_") and f.endswith(".db"))
    for viejo in archivos[:-guardar_ultimos]:
        os.remove(os.path.join(CARPETA_RESPALDOS, viejo))
    return destino