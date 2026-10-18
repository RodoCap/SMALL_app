from datetime import date


def _es_numero(valor):
    # int o float, pero no True/False (en Python bool también cuenta como int)
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)

def _es_entero(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


class Producto:
    def __init__(self, nombre, compra, venta, cantidad_comprada, id_producto, categoria):
        if not _es_entero(id_producto) or id_producto < 1:
            raise ValueError("El ID debe ser un número entero mayor a 0")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        if not _es_numero(compra):
            raise ValueError("El costo de compra debe ser un número")
        if not _es_numero(venta):
            raise ValueError("El precio de venta debe ser un número")
        if not _es_entero(cantidad_comprada):
            raise ValueError("Las unidades compradas deben ser un número entero")
        if compra < 0:
            raise ValueError("La compra no puede ser negativa")
        if venta < 0:
            raise ValueError("La venta no puede ser negativa")
        if cantidad_comprada < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self.nombre = nombre.strip()
        self.compra = compra
        self.venta = venta
        self.id_producto = id_producto
        self.categoria = categoria
        self.cantidad_comprada = cantidad_comprada
        self.cantidad_vendida = 0

    @property
    def stock_actual(self):
        return self.cantidad_comprada - self.cantidad_vendida

    @property
    def total_invertido(self):
        return round(self.compra * self.cantidad_comprada, 2)

    @property
    def ganancia_unitaria(self):
        # Ganancia por unidad al precio de lista (el real depende de cada venta)
        return round(self.venta - self.compra, 2)

    # OJO: el total vendido y la ganancia REAL de un producto ya no se calculan aquí,
    # porque cada venta puede tener un precio distinto. Salen de Inventario
    # (total_vendido_de / ganancia_de), sumando sus ventas.

    def actualizar(self, nombre, categoria, compra, venta, cantidad_comprada=None):
        # Primero valida y SOLO si todo está bien cambia los datos
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        if not _es_numero(compra):
            raise ValueError("El costo de compra debe ser un número")
        if not _es_numero(venta):
            raise ValueError("El precio de venta debe ser un número")
        if compra < 0:
            raise ValueError("La compra no puede ser negativa")
        if venta < 0:
            raise ValueError("La venta no puede ser negativa")
        if cantidad_comprada is not None:
            if not _es_entero(cantidad_comprada):
                raise ValueError("Las unidades compradas deben ser un número entero")
            if cantidad_comprada < self.cantidad_vendida:
                raise ValueError(f"Las unidades compradas no pueden ser menos de las {self.cantidad_vendida} ya vendidas")
            self.cantidad_comprada = cantidad_comprada
        self.nombre = nombre.strip()
        self.categoria = categoria
        self.compra = compra
        self.venta = venta

    def reponer(self, cantidad, costo=None):
        if not _es_entero(cantidad) or cantidad < 1:
            raise ValueError("La cantidad a reponer debe ser un número entero mayor a 0")
        if costo is not None:
            if not _es_numero(costo) or costo < 0:
                raise ValueError("El costo debe ser un número mayor o igual a 0")
            # Costo promedio de todo lo comprado: así total_invertido
            # sigue siendo la suma real de todas las compras
            total = self.compra * self.cantidad_comprada + costo * cantidad
            self.compra = round(total / (self.cantidad_comprada + cantidad), 2)
        self.cantidad_comprada += cantidad

    def mostrar_info(self):
        print("Nombre: ", self.nombre, "Compra: ", self.compra, "Venta: ", self.venta, "ID: ", self.id_producto, "Categoria: ", self.categoria, "Stock Actual: ", self.stock_actual)


class Venta:
    def __init__(self, fecha, producto, cantidad_vendida, precio_unitario, costo_unitario, id_producto=None, id_venta=None, id_credito=None):
        self.id_venta = id_venta  # lo asigna la base de datos al guardar
        self.fecha = fecha
        self.producto = producto
        self.precio_unitario = precio_unitario
        self.costo_unitario = costo_unitario
        self.cantidad_vendida = cantidad_vendida
        self.id_producto = id_producto
        self.id_credito = id_credito  # None = venta de contado

    @property
    def ganancia(self):
        return round((self.precio_unitario - self.costo_unitario) * self.cantidad_vendida, 2)

    @property
    def total(self):
        return round(self.cantidad_vendida * self.precio_unitario, 2)


class Abono:
    def __init__(self, fecha, monto, id_credito=None, id_abono=None):
        self.id_abono = id_abono
        self.id_credito = id_credito
        self.fecha = fecha
        self.monto = monto


class Credito:
    def __init__(self, cliente, fecha, fecha_proximo_pago=None, id_credito=None):
        self.id_credito = id_credito
        self.cliente = cliente
        self.fecha = fecha
        self.fecha_proximo_pago = fecha_proximo_pago  # texto AAAA-MM-DD o None
        self.ventas = []   # los productos que se llevó
        self.abonos = []   # lo que ha pagado

    @property
    def total(self):
        return round(sum(v.total for v in self.ventas), 2)

    @property
    def total_abonado(self):
        return round(sum(a.monto for a in self.abonos), 2)

    @property
    def saldo(self):
        return round(self.total - self.total_abonado, 2)

    @property
    def esta_pagado(self):
        return self.saldo <= 0

    @property
    def vencido(self):
        return (not self.esta_pagado
                and self.fecha_proximo_pago is not None
                and self.fecha_proximo_pago < date.today().isoformat())


class Inventario:
    def __init__(self):
        self.productos = []
        self.ventas = []
        self.creditos = []

    # ---------- Productos ----------
    def agregar_producto(self, producto):
        self.productos.append(producto)

    def listar_productos(self):
        for producto in self.productos:
            producto.mostrar_info()

    def buscar_producto(self, id_producto):
        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto
        return None

    def eliminar_producto(self, id_producto):
        producto = self.buscar_producto(id_producto)
        if producto:
            self.productos.remove(producto)
            print("Producto eliminado")
            return True
        else:
            return False

    # ---------- Ventas de un producto ----------
    def ventas_de(self, id_producto):
        return [v for v in self.ventas if v.id_producto == id_producto]

    def tuvo_ventas(self, id_producto):
        return len(self.ventas_de(id_producto)) > 0

    def total_vendido_de(self, id_producto):
        return round(sum(v.total for v in self.ventas_de(id_producto)), 2)

    def ganancia_de(self, id_producto):
        return round(sum(v.ganancia for v in self.ventas_de(id_producto)), 2)

    def precio_promedio_de(self, id_producto):
        ventas = self.ventas_de(id_producto)
        unidades = sum(v.cantidad_vendida for v in ventas)
        if unidades == 0:
            return None
        return sum(v.total for v in ventas) / unidades

    def buscar_venta(self, id_venta):
        for venta in self.ventas:
            if venta.id_venta == id_venta:
                return venta
        return None

    def anular_venta(self, id_venta):
        # Quita la venta y devuelve sus unidades al stock (si el producto aún existe)
        venta = self.buscar_venta(id_venta)
        if venta is None:
            return False
        producto = self.buscar_producto(venta.id_producto)
        if producto is not None:
            producto.cantidad_vendida = max(0, producto.cantidad_vendida - venta.cantidad_vendida)
        self.ventas.remove(venta)
        return True

    def registrar_venta(self, id_producto, cantidad, precio=None):
        producto = self.buscar_producto(id_producto)
        if producto is None:
            return False
        if not _es_entero(cantidad) or cantidad < 1:
            raise ValueError("La cantidad debe ser un número entero mayor a 0")
        if precio is None:
            precio = producto.venta  # sin precio especial: se vende al precio de lista
        elif not _es_numero(precio) or precio < 0:
            raise ValueError("El precio debe ser un número mayor o igual a 0")
        if cantidad > producto.stock_actual:
            raise ValueError("No hay suficiente stock")
        producto.cantidad_vendida += cantidad

        venta = Venta(
            fecha=date.today().isoformat(),
            producto=producto.nombre,
            cantidad_vendida=cantidad,
            precio_unitario=precio,
            costo_unitario=producto.compra,
            id_producto=producto.id_producto
        )
        self.ventas.append(venta)
        return True

    # ---------- Créditos ----------
    def buscar_credito(self, id_credito):
        for credito in self.creditos:
            if credito.id_credito == id_credito:
                return credito
        return None

    def registrar_credito(self, cliente, items, abono_inicial=0, fecha_proximo_pago=None):
        # Valida TODO primero; solo si todo está bien cambia stock y listas
        cliente = cliente.strip() if isinstance(cliente, str) else ""
        if not cliente:
            raise ValueError("El nombre del cliente no puede estar vacío")
        if not isinstance(items, list) or len(items) == 0:
            raise ValueError("El crédito debe tener al menos un producto")
        if fecha_proximo_pago is not None:
            try:
                date.fromisoformat(fecha_proximo_pago)
            except (TypeError, ValueError):
                raise ValueError("La fecha del próximo pago no es válida")

        pedido_por_producto = {}  # por si el mismo producto viene en dos líneas
        lineas = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Hay un producto con formato inválido")
            producto = self.buscar_producto(item.get("id_producto"))
            if producto is None:
                raise ValueError(f"El producto {item.get('id_producto')} no existe")
            cantidad = item.get("cantidad")
            if not _es_entero(cantidad) or cantidad < 1:
                raise ValueError("La cantidad debe ser un número entero mayor a 0")
            precio = item.get("precio")
            if precio is None:
                precio = producto.venta
            elif not _es_numero(precio) or precio < 0:
                raise ValueError("El precio debe ser un número mayor o igual a 0")
            pedido_por_producto[producto.id_producto] = pedido_por_producto.get(producto.id_producto, 0) + cantidad
            if pedido_por_producto[producto.id_producto] > producto.stock_actual:
                raise ValueError(f"No hay suficiente stock de {producto.nombre}")
            lineas.append((producto, cantidad, precio))

        total = round(sum(cantidad * precio for _, cantidad, precio in lineas), 2)
        if not _es_numero(abono_inicial) or abono_inicial < 0:
            raise ValueError("El abono debe ser un número mayor o igual a 0")
        if abono_inicial > total:
            raise ValueError("El abono no puede ser mayor al total del crédito")

        hoy = date.today().isoformat()
        credito = Credito(cliente, hoy, fecha_proximo_pago)
        for producto, cantidad, precio in lineas:
            producto.cantidad_vendida += cantidad
            venta = Venta(
                fecha=hoy,
                producto=producto.nombre,
                cantidad_vendida=cantidad,
                precio_unitario=precio,
                costo_unitario=producto.compra,
                id_producto=producto.id_producto
            )
            credito.ventas.append(venta)
            self.ventas.append(venta)
        if abono_inicial > 0:
            credito.abonos.append(Abono(hoy, abono_inicial))
        self.creditos.append(credito)
        return credito

    def registrar_abono(self, id_credito, monto):
        credito = self.buscar_credito(id_credito)
        if credito is None:
            return None
        if not _es_numero(monto) or monto <= 0:
            raise ValueError("El abono debe ser un número mayor a 0")
        if monto > credito.saldo:
            raise ValueError(f"El abono no puede ser mayor a lo que debe ({credito.saldo})")
        abono = Abono(date.today().isoformat(), monto, id_credito=credito.id_credito)
        credito.abonos.append(abono)
        return abono

    def anular_credito(self, id_credito):
        # Quita el crédito y sus ventas, y devuelve las unidades al stock
        credito = self.buscar_credito(id_credito)
        if credito is None:
            return False
        for venta in credito.ventas:
            producto = self.buscar_producto(venta.id_producto)
            if producto is not None:
                producto.cantidad_vendida = max(0, producto.cantidad_vendida - venta.cantidad_vendida)
            self.ventas.remove(venta)
        self.creditos.remove(credito)
        return True