from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Carrito, Categoria, Colaboradores, ItemCarrito, Perfil, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para categorías de productos."""

    class Meta:
        model = Categoria
        fields = ('id', 'nombre')


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador de producto con nombre de categoría legible y URL de imagen."""

    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = (
            'id',
            'nombre',
            'medida',
            'unidad',
            'precio',
            'stock',
            'descripcion',
            'categoria',
            'categoria_nombre',
            'marca',
            'imagen_url',
            'destacado',
            'aroma',
        )

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url


class ColaboradoresSerializer(serializers.ModelSerializer):
    """Serializador para colaboradores institucionales."""

    class Meta:
        model = Colaboradores
        fields = ('id', 'nombre_colaborador', 'descripcion', 'logo', 'enlace')


class PerfilSerializer(serializers.ModelSerializer):
    """Serializador del perfil de usuario con datos básicos de User."""

    username = serializers.CharField(source='usuario.username', read_only=True)
    first_name = serializers.CharField(source='usuario.first_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='usuario.email', required=False)

    class Meta:
        model = Perfil
        fields = (
            'id',
            'username',
            'first_name',
            'email',
            'telefono',
            'direccion',
            'comuna',
            'region',
        )

    def validate_email(self, value):
        email = value.strip().lower()
        usuario = self.instance.usuario if self.instance else None
        qs = User.objects.filter(email__iexact=email)
        if usuario:
            qs = qs.exclude(pk=usuario.pk)
        if qs.exists():
            raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('usuario', {})
        if usuario_data:
            usuario = instance.usuario
            if 'first_name' in usuario_data:
                usuario.first_name = usuario_data['first_name']
            if 'email' in usuario_data:
                usuario.email = usuario_data['email']
            usuario.save()

        return super().update(instance, validated_data)


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Serializador para registrar nuevos usuarios y crear su Perfil asociado."""

    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'email', 'password')

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Ya existe una cuenta con este correo electrónico.')
        return email

    def create(self, validated_data):
        usuario = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'].strip(),
        )
        Perfil.objects.get_or_create(usuario=usuario)
        return usuario


class ItemCarritoSerializer(serializers.ModelSerializer):
    """Serializador para ítems dentro del carrito."""

    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    precio_unitario = serializers.IntegerField(source='producto.precio', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ('id', 'producto', 'producto_nombre', 'precio_unitario', 'cantidad', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal()


class CarritoSerializer(serializers.ModelSerializer):
    """Serializador del carrito activo con sus ítems y total."""

    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ('id', 'tipo_envio', 'completado', 'creado_en', 'items', 'total')

    def get_total(self, obj):
        return sum(item.subtotal() for item in obj.items.all())
