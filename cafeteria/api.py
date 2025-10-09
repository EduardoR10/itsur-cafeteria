from rest_framework import viewsets, routers, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Prefetch
from .models import Producto, MenuDia, Orden, OrdenItem
from .serializers import ProductoSerializer, MenuDiaSerializer, OrdenSerializer

class ProductoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Producto.objects.filter(disponible=True).select_related('categoria')
    serializer_class = ProductoSerializer

class MenuDiaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = MenuDia.objects.filter(publicado=True)
    serializer_class = MenuDiaSerializer

    @action(detail=False, methods=['get'])
    def hoy(self, request):
        hoy = timezone.localdate()
        menu = MenuDia.objects.filter(fecha=hoy, publicado=True).first()
        if not menu:
            return Response({'detail':'Sin menú para hoy'}, status=404)
        return Response(MenuDiaSerializer(menu).data)

class OrdenViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = OrdenSerializer

    def get_queryset(self):
        qs = Orden.objects.all().order_by('creado').prefetch_related(
            Prefetch('items', queryset=OrdenItem.objects.select_related('producto'))
        )
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    @action(detail=True, methods=['patch'])
    def estado(self, request, pk=None):
        orden = self.get_queryset().get(pk=pk)
        nuevo = request.data.get('estado')
        validos = {e for e, _ in Orden.Estado.choices}
        if nuevo not in validos:
            return Response({'detail':'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
        orden.estado = nuevo
        orden.save()
        return Response(OrdenSerializer(orden).data)

router = routers.DefaultRouter()
router.register(r'products', ProductoViewSet, basename='product')
router.register(r'menu', MenuDiaViewSet, basename='menu')
router.register(r'orders', OrdenViewSet, basename='order')
