from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# NAVEGACIÓN 
def inicio(request):
    return render(request, "index.html")

def tienda(request, categoria=''):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    if categoria:
        productos = productos.filter(categoria__nombre=categoria)

    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    return render(request, 'tienda.html', {
        'productos': productos,
        'categorias': categorias,
        'categoriaActual': categoria,
        'busqueda': busqueda,
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
    return render(request, "nosotros.html")

def colaboradores(request):
    return render(request, "colaboradores.html")

def ciencia(request):
    return render(request, "ciencia.html")

def contacto(request):
    return render(request, "contacto.html")


# GESTION DE USUARIO (User de Django)
def registro_view(request):
    # Si ya está logueado, lo redirigimos al inicio
    if request.user.is_authenticated:
        return redirect('inicio')
        
    if request.method == 'POST':
        # Instanciamos el formulario nativo con los datos enviados por POST
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            # Creamos y guardamos el usuario de forma segura (contraseña hasheada)
            usuario = form.save()
            # Lo logueamos automáticamente tras registrarse con éxito
            auth_login(request, usuario)
            return redirect('inicio')
    else:
        # Formulario vacío para la primera carga
        form = UserCreationForm()
        
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    # Si ya está logueado, lo mandamos al inicio
    if request.user.is_authenticated:
        return redirect('inicio')
        
    if request.method == 'POST':
        # Le pasamos los datos al formulario nativo de Django
        form = AuthenticationForm(data=request.POST)
        
        # is_valid() se encarga de verificar que el correo y contraseña sean correctos
        if form.is_valid():
            # Extraemos el usuario validado y lo logueamos
            usuario = form.get_user()
            auth_login(request, usuario)
            return redirect('inicio')
    else:
        # Si entra por primera vez, mostramos el formulario vacío
        form = AuthenticationForm()
        
    # Mandamos el formulario nativo al HTML
    return render(request, 'login.html', {'form': form})

def perfil(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'perfil.html')

def editarPerfil(request):
    return render(request, 'perfil.html')

def cerrarSesion(request):
    if request.method == 'POST':
        logout(request) # Cierra la sesión nativa de Django
        return render(request, 'logout.html') 
    return redirect('inicio')

#CARRTIO
def carrito(request):
    return render(request, "index.html")

def agregarCarrito(request, pk):
    return render(request, "index.html")