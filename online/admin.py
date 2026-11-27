from django.contrib import admin
from .models import Producto, Categoria, Colaboradores
# Register your models here.

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Colaboradores)  # para editar ANID, CORFO y futuros colaboradores desde el panel
