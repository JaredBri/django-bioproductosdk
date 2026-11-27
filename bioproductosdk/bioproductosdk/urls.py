from django.contrib import admin
from django.urls import path
from online import views
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
