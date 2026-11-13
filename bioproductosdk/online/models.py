from django.db import models
from django.contrib.auth.models import User

# Productos de la librería
class Producto(models.Model):
    nombre = models.CharField(max_length=20)
    medida = models.FloatField(blank=True, null=True)
    precio = models.IntegerField()
    stock = models.IntegerField()
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50)
    marca = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre

class Impuestos(models.Model):
    iva = models.FloatField()
    despacho = models.IntegerField()
    region = models.CharField()

    def __str__(self):
        return f'IVA: {self.iva} - Región: {self.region} - Despacho:{self.despacho}'

# Carrito de compras
class Carrito(models.Model):
    TIPOS_ENVIO = [
        ('retiro', 'Retiro en tienda'),
        ('despacho', 'Despacho a domicilio')
        ('envio_express', 'Despacho Express'),
    ]
    tipo_envio = models.CharField(max_length=20,choices=TIPOS_ENVIO,default='retiro')
    usuario = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"Carrito {self.id} - Usuario: {self.usuario}"


# Productos agregados al carrito
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito,on_delete=models.CASCADE,related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.producto.precio * self.cantidad


class Colaboradores(models.Model):
    nombre_colaborador = models.CharField(max_length=100)

