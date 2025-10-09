from rest_framework import serializers
from .models import Producto, MenuDia, MenuItem, Orden, OrdenItem

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id','nombre','precio','disponible','categoria']

class MenuItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()
    class Meta:
        model = MenuItem
        fields = ['producto','destacado']

class MenuDiaSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(source='menuitem_set', many=True)
    class Meta:
        model = MenuDia
        fields = ['fecha','publicado','items']

class OrdenItemSerializer(serializers.ModelSerializer):
    producto = serializers.StringRelatedField()
    class Meta:
        model = OrdenItem
        fields = ['producto','cantidad','precio_unitario','subtotal']

class OrdenSerializer(serializers.ModelSerializer):
    items = OrdenItemSerializer(many=True)
    class Meta:
        model = Orden
        fields = ['id','folio','estado','total','creado','items']
