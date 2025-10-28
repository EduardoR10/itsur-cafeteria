from rest_framework import serializers
from .models import (
    Categoria, Producto,
    MenuDia, MenuItem,
    Orden, OrdenItem
)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'activa']

class ProductoSerializer(serializers.ModelSerializer):
    categoria_detalle = CategoriaSerializer(source='categoria', read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'disponible', 'categoria', 'categoria_detalle']

class MenuItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all(),
                                                     source='producto',
                                                     write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'producto', 'producto_id', 'destacado']

class MenuDiaSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(source='menuitem_set', many=True, read_only=True)

    class Meta:
        model = MenuDia
        fields = ['id', 'fecha', 'publicado', 'items']

# --------- Orden & Items ----------

class OrdenItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenItem
        fields = ['id', 'producto', 'cantidad', 'precio_unitario', 'subtotal']

class OrdenItemReadSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = OrdenItem
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']

class OrdenSerializer(serializers.ModelSerializer):
    items = OrdenItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Orden
        fields = ['id', 'folio', 'estado', 'total', 'creado', 'creada_por', 'items']
        read_only_fields = ['total', 'creado', 'creada_por']

class OrdenCreateUpdateSerializer(serializers.ModelSerializer):

    items = OrdenItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Orden
        fields = ['id', 'folio', 'estado', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user if self.context and self.context.get('request') and self.context['request'].user.is_authenticated else None
        orden = Orden.objects.create(creada_por=user, **validated_data)
        for it in items_data:
            OrdenItem.objects.create(orden=orden, **it)
        return orden

    def update(self, instance, validated_data):
    
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for it in items_data:
                OrdenItem.objects.create(orden=instance, **it)

        return instance
