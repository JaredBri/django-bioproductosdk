from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)  # antes 20: no cabía "Detergente líquido biodegradable Cítrico"
    medida = models.FloatField(blank=True, null=True)
    unidad = models.CharField(max_length=10, blank=True)  # NUEVO: ml, L, g, kg... acompaña a medida
    precio = models.IntegerField()
    stock = models.PositiveIntegerField()
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    marca = models.CharField(max_length=20)
    # NUEVO: nombre del archivo dentro de online/static/images/ (ej: detergenteCitrico.jpg)
    imagen = models.ImageField(upload_to='productos/', max_length=100, blank=True)
    # NUEVO: marcar para que aparezca en "Productos destacados" de la página principal
    destacado = models.BooleanField(default=False)
    aroma = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Limpia espacios extra y deja la primera letra en mayúscula
        if self.marca:
            self.marca = self.marca.strip().capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Impuestos(models.Model):
    iva = models.FloatField()
    despacho = models.IntegerField()
    region = models.CharField(max_length=60)  # se agregó max_length (MySQL lo exige)
    # aunque usermos postgreSQL usare Mysql con XAMMP solo para ver el resultado de los templates
    # de forma momentane, despues de debe cambiar en settings.py/DATABASE 

    def __str__(self):
        return f'IVA: {self.iva} - Región: {self.region} - Despacho:{self.despacho}'

class Carrito(models.Model):
    TIPOS_ENVIO = [
        ('retiro', 'Retiro en tienda'),
        ('despacho', 'Despacho a domicilio'),
        ('envio_express', 'Despacho Express'),
    ]
    tipo_envio = models.CharField(max_length=20, choices=TIPOS_ENVIO, default='retiro')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"Carrito {self.id} - Usuario: {self.usuario}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.producto.precio * self.cantidad

class Colaboradores(models.Model):
    nombre_colaborador = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)             # NUEVO: texto breve de la colaboración
    logo = models.CharField(max_length=100, blank=True)    # NUEVO: archivo dentro de online/static/images/
    enlace = models.URLField(blank=True)                   # NUEVO: sitio web del colaborador

    def __str__(self):
        return self.nombre_colaborador

# NUEVO: datos de contacto y despacho del usuario (RFU003, perfil.html y editarPerfil.html)
# En los templates se usa como user.perfil.telefono, user.perfil.direccion, etc.
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=150, blank=True)
    comuna = models.CharField(max_length=60, blank=True)
    region = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"Perfil de {self.usuario}"