from django.contrib import admin
from django.urls import path
from online import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # NAVEGACIÓN
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('tienda/', views.tienda, name='tienda'),
    path('detalleProducto/<int:id>/', views.detalleProducto, name='detalleProducto'),
    path('tienda/categoria/<str:categoria>/', views.tienda, name='tiendaCategoria'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('colaboradores/', views.colaboradores, name='colaboradores'),
    path('ciencia/', views.ciencia, name='ciencia'),
    path('contacto/', views.contacto, name='contacto'),

    #GESTION DE USUARIO
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', views.logout, name='logout'),

    #CARRITO
    path('carrito/', views.carrito, name='carrito'),
    path('agregarCarrito/<int:id>', views.agregarCarrito, name='agregarCarrito'),
]
