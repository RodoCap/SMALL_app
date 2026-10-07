class Producto:
    def __init__(self, nombre, compra, venta, cantidad_comprada, id_producto, categoria):
        if compra < 0:
            raise ValueError("La compra no puede ser negativa")
        elif venta < 0:
            raise ValueError("La venta no puede ser negativa")
        elif cantidad_comprada < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self.nombre = nombre
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
        return self.compra * self.cantidad_comprada 

    @property
    def ganancia(self): 
        return (self.venta- self.compra) * self.cantidad_vendida 
    
    def mostrar_info(self):
        print("Nombre: ", self.nombre, "Compra: ", self.compra, "Venta: ", self.venta, "ID: ", self.id_producto, "Categoria: ", self.categoria,"Stock Actual: ",self.stock_actual)

    
   
class Inventario:
    def __init__(self):
        self.productos = []
        self.ventas = []

    def agregar_producto(self,producto): 
        self.productos.append(producto)

    def listar_productos(self):
        for producto in self.productos:
            producto.mostrar_info()

    def buscar_producto(self, id_producto):
        for producto in self.productos:
            if producto.id_producto == id_producto:
             return producto
        return None

    def eliminar_producto(self,id_producto): 
        producto = self.buscar_producto(id_producto)
        if producto: 
            self.productos.remove(producto)
            print("Producto eliminado")
            return True 
        else: 
            return False 
    
    def registrar_venta(self, id_producto, cantidad):
        producto = self.buscar_producto(id_producto)
        if producto is None:
            return False
        if cantidad > producto.stock_actual:
            raise ValueError("No hay suficiente stock")
        producto.cantidad_vendida += cantidad

        venta = Venta(
            fecha="2026-10-06",
            producto=producto.nombre,
            cantidad_vendida=cantidad,
            precio_unitario=producto.venta,
            costo_unitario=producto.compra
        )
        self.ventas.append(venta)
        return True

class Venta: 
    def __init__(self,fecha,producto,cantidad_vendida,precio_unitario,costo_unitario):
        self.fecha = fecha 
        self.producto = producto 
        self.precio_unitario = precio_unitario
        self.costo_unitario = costo_unitario
        self.cantidad_vendida = cantidad_vendida

    @property
    def ganancia(self): 
        return (self.precio_unitario - self.costo_unitario) *self.cantidad_vendida 

    @property 
    def total(self):
        return self.cantidad_vendida * self.precio_unitario

        
    

