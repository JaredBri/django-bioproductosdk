from django.shortcuts import render, get_object_or_404
from .models import Producto

# NAVEGACIÓN 
def index(request):
    return render(request, "index.html")

def inicio(request):
    return render(request, "index.html")

def tienda(request, categoria=''):
    productos = Producto.objects.all()
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    return render(request, 'tienda.html', {
        'productos': productos,
        'categorias': categorias,
        'categoriaActual': categoria,
    })

def detalleProducto(request, id):
    # Obtiene el producto específico o muestra un error 404 si no existe
    producto = get_object_or_404(Producto, pk=id)
    
    # Busca productos relacionados de la misma categoría (excluyendo el actual, máximo 4)
    productosRelacionados = Producto.objects.filter(categoria=producto.categoria).exclude(pk=producto.id)[:4]
    
    return render(request, 'detalleproducto.html', {
        'producto': producto,
        'productosRelacionados': productosRelacionados,
    })
    
def nosotros(request):
    return render(request, "index.html")

def colaboradores(request):
    return render(request, "index.html")

def ciencia(request):
    return render(request, "index.html")

def contacto(request):
    return render(request, "index.html")



# GESTION DE USUARIO (User de Django)
def registro(request):
    return render(request, "index.html")

def login(request):
    return render(request, "index.html")

def perfil(request):
    return render(request, "index.html")

def logout(request):
    return render(request, "index.html")

#CARRTIO
def carrito(request):
    return render(request, "index.html")

def agregarCarrito(request, pk):
    return render(request, "index.html")