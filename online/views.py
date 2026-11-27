from django.contrib import messages
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .context_processors import obtener_carrito_activo
from .forms import ContactoForm, LoginForm, PerfilForm, RegistroForm, UsuarioUpdateForm
from .models import Carrito, Categoria, Colaboradores, Impuestos, ItemCarrito, Perfil, Producto


def _fusionar_carrito_sesion(request, usuario):
    """Transfiere ítems de un carrito anónimo de sesión al carrito del usuario autenticado."""
    carrito_id = request.session.get('carrito_id')
    if not carrito_id:
        return
    carrito_sesion = Carrito.objects.filter(id=carrito_id, usuario__isnull=True).first()
    if not carrito_sesion:
        return

    carrito_usuario, _ = Carrito.objects.get_or_create(usuario=usuario)
    for item_sesion in carrito_sesion.items.select_related('producto').all():
        item_usuario, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito_usuario,
            producto=item_sesion.producto,
            defaults={'cantidad': 0},
        )
        nueva_cantidad = item_usuario.cantidad + item_sesion.cantidad
        item_usuario.cantidad = min(nueva_cantidad, item_sesion.producto.stock)
        if item_usuario.cantidad > 0:
            item_usuario.save()
        elif creado:
            item_usuario.delete()

    carrito_sesion.delete()
    request.session.pop('carrito_id', None)


# NAVEGACIÓN
def inicio(request):
    productosDestacados = Producto.objects.filter(destacado=True)[:4]
    colaboradores = Colaboradores.objects.all()
    return render(request, "index.html", {
        'productosDestacados': productosDestacados,
        'colaboradores': colaboradores,
    })


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
    producto = get_object_or_404(Producto, pk=id)
    productosRelacionados = Producto.objects.filter(categoria=producto.categoria).exclude(pk=producto.id)[:4]

    return render(request, 'detalleproducto.html', {
        'producto': producto,
        'productosRelacionados': productosRelacionados,
    })


def nosotros(request):
    return render(request, "nosotros.html")


def colaboradores(request):
    return render(request, "colaboradores.html", {
        'colaboradores': Colaboradores.objects.all(),
    })


def ciencia(request):
    return render(request, "ciencia.html")


def contacto(request):
    tipo_inicial = 'B2C / Cliente'
    if request.GET.get('tipo') == 'distribuidor':
        tipo_inicial = 'Biodistribuidor DK'

    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            messages.success(
                request,
                f"¡Gracias, {form.cleaned_data['nombre']}! Recibimos tu consulta sobre \"{form.cleaned_data['tipo_consulta']}\" y te responderemos a la brevedad."
            )
            return redirect('contacto')
        messages.error(request, 'Por favor revisa los campos marcados antes de enviar.')
    else:
        form = ContactoForm(initial={'tipo_consulta': tipo_inicial})

    return render(request, "contacto.html", {'form': form})


# GESTIÓN DE USUARIO (User de Django)
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = RegistroForm(data=request.POST)
        if form.is_valid():
            usuario = form.save()
            _fusionar_carrito_sesion(request, usuario)
            auth_login(request, usuario)
            messages.success(request, f'¡Bienvenido/a a BioProductos DK, {usuario.first_name or usuario.username}!')
            return redirect('inicio')
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            _fusionar_carrito_sesion(request, usuario)
            auth_login(request, usuario)
            messages.success(request, f'¡Qué bueno verte de nuevo, {usuario.first_name or usuario.username}!')
            return redirect('inicio')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def perfil(request):
    if not request.user.is_authenticated:
        return redirect('login')
    Perfil.objects.get_or_create(usuario=request.user)
    return render(request, 'perfil.html')


@login_required(login_url='login')
def editarPerfil(request):
    perfil_usuario, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        usuario_form = UsuarioUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, instance=perfil_usuario)
        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, 'Tus datos personales y de despacho se guardaron correctamente.')
            return redirect('perfil')
        messages.error(request, 'Por favor corrige los errores indicados en el formulario.')
    else:
        usuario_form = UsuarioUpdateForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil_usuario)

    return render(request, 'editarPerfil.html', {
        'usuarioForm': usuario_form,
        'perfilForm': perfil_form,
    })


def cerrarSesion(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'logout.html')
    return redirect('inicio')


# CARRITO DE COMPRAS
def _calcular_resumen_carrito(request, carrito):
    items = list(carrito.items.select_related('producto', 'producto__categoria').all()) if carrito else []
    subtotal = sum(item.subtotal() for item in items)

    impuesto = None
    if request.user.is_authenticated:
        perfil_usuario = Perfil.objects.filter(usuario=request.user).first()
        if perfil_usuario and perfil_usuario.region:
            impuesto = Impuestos.objects.filter(region__iexact=perfil_usuario.region).first()
    if not impuesto:
        impuesto = Impuestos.objects.first()

    tasa_iva = impuesto.iva if impuesto else 0.19
    if tasa_iva > 1:
        tasa_iva = tasa_iva / 100.0
    iva_monto = round(subtotal * tasa_iva / (1 + tasa_iva)) if subtotal > 0 else 0

    costo_despacho = 0
    if carrito and items:
        base_despacho = impuesto.despacho if impuesto else 3990
        if carrito.tipo_envio == 'despacho':
            costo_despacho = base_despacho
        elif carrito.tipo_envio == 'envio_express':
            costo_despacho = round(base_despacho * 1.5)

    total = subtotal + costo_despacho
    return {
        'items': items,
        'subtotal': subtotal,
        'iva': iva_monto,
        'porcentajeIva': round(tasa_iva * 100),
        'costoDespacho': costo_despacho,
        'total': total,
        'impuesto': impuesto,
    }


def carrito(request):
    carrito_actual = obtener_carrito_activo(request, crear=False)

    if request.method == 'POST' and carrito_actual:
        tipo_envio = request.POST.get('tipo_envio')
        if tipo_envio in dict(Carrito.TIPOS_ENVIO):
            carrito_actual.tipo_envio = tipo_envio
            carrito_actual.save()
            messages.success(request, 'Método de envío actualizado.')
        return redirect('carrito')

    resumen = _calcular_resumen_carrito(request, carrito_actual)
    return render(request, "carrito.html", {
        'carrito': carrito_actual,
        'tiposEnvio': Carrito.TIPOS_ENVIO,
        **resumen,
    })


def agregarCarrito(request, id):
    producto = get_object_or_404(Producto, pk=id)
    if request.method != 'POST':
        return redirect('detalleProducto', id=producto.id)

    if producto.stock <= 0:
        messages.error(request, f'"{producto.nombre}" se encuentra agotado.')
        return redirect('detalleProducto', id=producto.id)

    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1
    if cantidad < 1:
        cantidad = 1

    carrito_actual = obtener_carrito_activo(request, crear=True)
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito_actual,
        producto=producto,
        defaults={'cantidad': 0},
    )

    nueva_cantidad = item.cantidad + cantidad
    if nueva_cantidad > producto.stock:
        if creado:
            item.delete()
        messages.warning(
            request,
            f'Solo hay {producto.stock} unidades disponibles de "{producto.nombre}".'
        )
        return redirect(request.POST.get('next') or 'carrito')

    item.cantidad = nueva_cantidad
    item.save()
    messages.success(request, f'Se agregó "{producto.nombre}" a tu carrito.')
    return redirect(request.POST.get('next') or 'carrito')


def actualizarCarrito(request, item_id):
    if request.method != 'POST':
        return redirect('carrito')

    carrito_actual = obtener_carrito_activo(request, crear=False)
    if not carrito_actual:
        return redirect('carrito')

    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=carrito_actual)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = item.cantidad

    if cantidad <= 0:
        nombre = item.producto.nombre
        item.delete()
        messages.info(request, f'Se eliminó "{nombre}" del carrito.')
    elif cantidad > item.producto.stock:
        messages.warning(
            request,
            f'Stock insuficiente: solo quedan {item.producto.stock} unidades de "{item.producto.nombre}".'
        )
    else:
        item.cantidad = cantidad
        item.save()
        messages.success(request, f'Cantidad de "{item.producto.nombre}" actualizada a {cantidad}.')

    return redirect('carrito')


def eliminarCarrito(request, item_id):
    if request.method != 'POST':
        return redirect('carrito')

    carrito_actual = obtener_carrito_activo(request, crear=False)
    if not carrito_actual:
        return redirect('carrito')

    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=carrito_actual)
    nombre = item.producto.nombre
    item.delete()
    messages.info(request, f'Se eliminó "{nombre}" del carrito.')
    return redirect('carrito')


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT — datos de envío y resumen final antes del pago
# ─────────────────────────────────────────────────────────────────────────────

from django.contrib.auth.decorators import login_required as _login_required


@_login_required(login_url='login')
def checkout(request):
    """
    Paso 1 del pago: muestra el resumen del pedido, los datos de despacho del
    usuario y permite confirmar antes de simular el cobro.
    Requiere sesión activa y al menos un ítem en el carrito.
    """
    carrito_actual = obtener_carrito_activo(request, crear=False)
    if not carrito_actual or not carrito_actual.items.exists():
        messages.warning(request, 'Tu carrito está vacío. Agrega productos antes de continuar.')
        return redirect('carrito')

    resumen = _calcular_resumen_carrito(request, carrito_actual)
    perfil_usuario = Perfil.objects.filter(usuario=request.user).first()

    return render(request, 'checkout.html', {
        'carrito': carrito_actual,
        'perfil': perfil_usuario,
        'tiposEnvio': Carrito.TIPOS_ENVIO,
        **resumen,
    })


@_login_required(login_url='login')
def procesarPago(request):
    """
    Paso 2: procesa el pago simulado (POST desde checkout.html).
    Marca el carrito como completado, descuenta stock y muestra la
    página de confirmación con el número de pedido.
    """
    if request.method != 'POST':
        return redirect('checkout')

    carrito_actual = obtener_carrito_activo(request, crear=False)
    if not carrito_actual or not carrito_actual.items.exists():
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('carrito')

    # --- Validar método de pago seleccionado ---
    metodo_pago = request.POST.get('metodo_pago', 'simulado')
    metodos_validos = ('transferencia', 'debito', 'credito', 'simulado')
    if metodo_pago not in metodos_validos:
        metodo_pago = 'simulado'

    # --- Descontar stock ---
    for item in carrito_actual.items.select_related('producto').all():
        producto = item.producto
        if item.cantidad > producto.stock:
            messages.error(
                request,
                f'Stock insuficiente para "{producto.nombre}". '
                f'Solo quedan {producto.stock} unidades.'
            )
            return redirect('carrito')
        producto.stock = max(producto.stock - item.cantidad, 0)
        producto.save()

    # --- Calcular resumen para la confirmación ---
    resumen = _calcular_resumen_carrito(request, carrito_actual)
    items_confirmados = list(carrito_actual.items.select_related('producto').all())
    tipo_envio_display = carrito_actual.get_tipo_envio_display()

    # --- Marcar como completado y generar número de pedido ---
    import datetime, hashlib
    carrito_actual.completado = True
    carrito_actual.save()

    # Número de pedido: fecha + hash corto del id
    fecha_str = datetime.datetime.now().strftime('%Y%m%d')
    hash_corto = hashlib.md5(str(carrito_actual.id).encode()).hexdigest()[:6].upper()
    numero_pedido = f'BDK-{fecha_str}-{hash_corto}'

    # Limpiar carrito de sesión para que se cree uno nuevo en la próxima compra
    request.session.pop('carrito_id', None)

    return render(request, 'confirmacion.html', {
        'numero_pedido': numero_pedido,
        'items': items_confirmados,
        'metodo_pago': metodo_pago,
        'tipo_envio': tipo_envio_display,
        **resumen,
    })
