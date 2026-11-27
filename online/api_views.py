from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Carrito, Categoria, Colaboradores, Perfil, Producto
from .serializers import (
    CarritoSerializer,
    CategoriaSerializer,
    ColaboradoresSerializer,
    PerfilSerializer,
    ProductoSerializer,
    RegistroUsuarioSerializer,
)


class ProductoListAPIView(generics.ListAPIView):
    """Lista productos con soporte de filtro ?categoria= y búsqueda ?search=."""

    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Producto.objects.select_related('categoria').all().order_by('id')
        categoria = self.request.query_params.get('categoria')
        search = self.request.query_params.get('search')

        if categoria:
            if categoria.isdigit():
                queryset = queryset.filter(categoria_id=int(categoria))
            else:
                queryset = queryset.filter(categoria__nombre__iexact=categoria)

        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        return queryset


class ProductoDetailAPIView(generics.RetrieveAPIView):
    """Detalle de un producto por ID."""

    queryset = Producto.objects.select_related('categoria').all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoriaListAPIView(generics.ListAPIView):
    """Lista todas las categorías disponibles."""

    queryset = Categoria.objects.all().order_by('id')
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ColaboradoresListAPIView(generics.ListAPIView):
    """Lista los colaboradores institucionales."""

    queryset = Colaboradores.objects.all().order_by('id')
    serializer_class = ColaboradoresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RegistroUsuarioAPIView(generics.CreateAPIView):
    """Registro de nuevos clientes vía API REST."""

    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return Response(
            {
                'id': usuario.id,
                'username': usuario.username,
                'first_name': usuario.first_name,
                'email': usuario.email,
            },
            status=status.HTTP_201_CREATED,
        )


class PerfilAPIView(APIView):
    """Lectura y actualización del perfil del usuario autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        serializer = PerfilSerializer(perfil)
        return Response(serializer.data)

    def put(self, request):
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        serializer = PerfilSerializer(perfil, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CarritoAPIView(APIView):
    """Lectura del carrito activo del usuario autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)
