from django.shortcuts import get_object_or_404
from .domain.logic import CalculadorImpuestos

from .models import Libro, Inventario
from .domain.builders import OrdenBuilder


class CompraService:
    def __init__(self, procesador_pago):
        self.procesador = procesador_pago
        self.builder = OrdenBuilder()

    def ejecutar_proceso_compra(self, usuario, lista_productos, direccion):
        if not lista_productos:
            raise ValueError("No hay productos para comprar.")

        libro = lista_productos[0]
        inventario = Inventario.objects.get(libro=libro)

        if inventario.cantidad <= 0:
            raise ValueError("No hay existencias.")

        orden = (
            self.builder
            .con_usuario(usuario)
            .con_productos(lista_productos)
            .para_envio(direccion)
            .build()
        )

        if self.procesador.pagar(orden.total):
            inventario.cantidad -= 1
            inventario.save()
            return orden.total

        orden.delete()
        raise Exception("Error en la pasarela de pagos.")

    def ejecutar_compra(self, libro_id, direccion, usuario):
        libro = Libro.objects.get(id=libro_id)
        return self.ejecutar_proceso_compra(
            usuario=usuario,
            lista_productos=[libro],
            direccion=direccion
        )
    

class CompraRapidaService:
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def procesar(self, libro_id):
        libro = Libro.objects.get(id=libro_id)
        inv = Inventario.objects.get(libro=libro)

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if self.procesador_pago.pagar(total):
            inv.cantidad -= 1
            inv.save()
            return total

        return None
