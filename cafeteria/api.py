from rest_framework import viewsets, routers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Prefetch

from .models import (
    Categoria, Producto,
    MenuDia, MenuItem,
    Orden, OrdenItem
)
from .serializers import (
    CategoriaSerializer, ProductoSerializer,
    MenuDiaSerializer, MenuItemSerializer,
    OrdenSerializer, OrdenCreateUpdateSerializer,
    OrdenItemReadSerializer, OrdenItemWriteSerializer
)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria').all().order_by('nombre')
        categoria = self.request.query_params.get('categoria')
        disponible = self.request.query_params.get('disponible')
        q = self.request.query_params.get('q')
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        if disponible in ('true', 'false'):
            qs = qs.filter(disponible=(disponible == 'true'))
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

class MenuDiaViewSet(viewsets.ModelViewSet):
    queryset = MenuDia.objects.all().order_by('-fecha')
    serializer_class = MenuDiaSerializer

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        hoy = timezone.localdate()
        menu = MenuDia.objects.filter(fecha=hoy, publicado=True).first()
        if not menu:
            return Response({'detail': 'Sin menú para hoy'}, status=404)
        return Response(MenuDiaSerializer(menu).data)

    @action(detail=True, methods=['post'])
    def agregar_item(self, request, pk=None):
        menu = self.get_object()
        ser = MenuItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=201)

class OrdenViewSet(viewsets.ModelViewSet):
    queryset = (Orden.objects
                .order_by('-creado')
                .prefetch_related(Prefetch('items', queryset=OrdenItem.objects.select_related('producto'))))

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrdenCreateUpdateSerializer
        return OrdenSerializer

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        orden = self.get_object()
        data = OrdenItemReadSerializer(orden.items.all(), many=True).data
        return Response(data)

class OrdenItemViewSet(viewsets.ModelViewSet):
    queryset = OrdenItem.objects.select_related('orden', 'producto').all().order_by('-id')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrdenItemReadSerializer
        return OrdenItemWriteSerializer

router = routers.DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'menu', MenuDiaViewSet, basename='menu')
router.register(r'ordenes', OrdenViewSet, basename='orden')
router.register(r'orden-items', OrdenItemViewSet, basename='ordenitem')
