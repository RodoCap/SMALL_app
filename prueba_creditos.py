import os, tempfile
import database
database.RUTA_DB = os.path.join(tempfile.mkdtemp(), "prueba.db")

from models import Producto, Inventario

database.crear_tablas_creditos()
inv = Inventario()
for p in (Producto("Cable USB-C", 5000, 12000, 10, 1, "Cables"),
          Producto("Audífonos", 20000, 45000, 5, 2, "Audífonos")):
    inv.agregar_producto(p)
    database.insertar_producto(p)

c = inv.registrar_credito(
    "Juan",
    [{"id_producto": 1, "cantidad": 2}, {"id_producto": 2, "cantidad": 1, "precio": 40000}],
    abono_inicial=30000, fecha_proximo_pago="2026-10-30")
database.guardar_credito(c)
print(c.total, c.saldo)            # esperado: 64000 34000

a = inv.registrar_abono(c.id_credito, 34000)
database.guardar_abono(a)
print(c.saldo, c.esta_pagado)      # esperado: 0 True

recarga = database.obtener_creditos(database.obtener_ventas())
print(recarga[0].cliente, recarga[0].saldo)  # esperado: Juan 0