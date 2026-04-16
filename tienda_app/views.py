from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View

from .models import Libro
from .infra.factories import PaymentFactory
from .services import CompraService

from django.contrib.auth.models import User


class CompraView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = float(libro.precio) * 1.19

        return render(request, self.template_name, {
            'libro': libro,
            'total': total
        })

    def post(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        service = self.setup_service()
        usuario = User.objects.get(username="alejo_test")

        try:
            mensaje = service.ejecutar_proceso_compra(
                usuario=usuario,
                lista_productos=[libro],
                direccion="Medellín"
            )
            return HttpResponse(mensaje)
        except Exception as e:
            print("ERROR EN COMPRA:", repr(e))
            return HttpResponse(str(e), status=400)


class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = float(libro.precio) * 1.19
        return render(request, self.template_name, {
            'libro': libro,
            'total': total
        })

    def post(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = Inventario.objects.get(libro=libro)
        if inv.cantidad > 0:
            total = float(libro.precio) * 1.19
            return HttpResponse("Comprado via CBV")
        return HttpResponse("Error", status=400)
