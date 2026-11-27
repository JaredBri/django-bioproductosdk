from django.contrib import admin
from django.urls import path
from online import api_views, views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # NAVEGACIÓN
    path('', views.inicio, name='inicio'),
    path('tienda/', views.tienda, name='tienda'),
    path('detalleProducto/<int:id>/', views.detalleProducto, name='detalleProducto'),
    path('tienda/categoria/<str:categoria>/', views.tienda, name='tiendaCategoria'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('colaboradores/', views.colaboradores, name='colaboradores'),
    path('ciencia/', views.ciencia, name='ciencia'),
    path('contacto/', views.contacto, name='contacto'),

    #GESTION DE USUARIO
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('editarPerfil/', views.editarPerfil, name='editarPerfil'),

    #CARRITO
    path('carrito/', views.carrito, name='carrito'),
    path('agregarCarrito/<int:id>', views.agregarCarrito, name='agregarCarrito'),
    path('actualizarCarrito/<int:item_id>/', views.actualizarCarrito, name='actualizarCarrito'),
    path('eliminarCarrito/<int:item_id>/', views.eliminarCarrito, name='eliminarCarrito'),

    # CHECKOUT Y PAGO SIMULADO
    path('checkout/', views.checkout, name='checkout'),
    path('procesarPago/', views.procesarPago, name='procesarPago'),

    # API REST v1
    path('api/v1/productos/', api_views.ProductoListAPIView.as_view(), name='api_productos_lista'),
    path('api/v1/productos/<int:pk>/', api_views.ProductoDetailAPIView.as_view(), name='api_producto_detalle'),
    path('api/v1/categorias/', api_views.CategoriaListAPIView.as_view(), name='api_categorias_lista'),
    path('api/v1/colaboradores/', api_views.ColaboradoresListAPIView.as_view(), name='api_colaboradores_lista'),
    path('api/v1/auth/registro/', api_views.RegistroUsuarioAPIView.as_view(), name='api_registro'),
    path('api/v1/perfil/', api_views.PerfilAPIView.as_view(), name='api_perfil'),
    path('api/v1/carrito/', api_views.CarritoAPIView.as_view(), name='api_carrito'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
