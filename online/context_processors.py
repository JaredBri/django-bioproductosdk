from django.db.models import Sum
from .models import Carrito


def obtener_carrito_activo(request, crear=False):
    """Obtiene el carrito activo del usuario autenticado o de la sesión anónima."""
    if request.user.is_authenticated:
        if crear:
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
            return carrito
        return Carrito.objects.filter(usuario=request.user).first()

    carrito_id = request.session.get('carrito_id')
    if carrito_id:
        carrito = Carrito.objects.filter(id=carrito_id, usuario__isnull=True).first()
        if carrito:
            return carrito

    if crear:
        carrito = Carrito.objects.create()
        request.session['carrito_id'] = carrito.id
        return carrito
    return None


def carrito_context(request):
    """Expone la cantidad total de unidades en el carrito para la barra de navegación."""
    carrito = obtener_carrito_activo(request, crear=False)
    if not carrito:
        return {'cantidadCarrito': 0}

    total = carrito.items.aggregate(total=Sum('cantidad'))['total'] or 0
    return {'cantidadCarrito': total}
