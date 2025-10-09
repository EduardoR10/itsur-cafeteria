from django.contrib import admin
from .models import Categoria, Producto, MenuDia, MenuItem, Orden, OrdenItem, Pago

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre','activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre','categoria','precio','disponible')
    list_filter = ('categoria','disponible')
    search_fields = ('nombre',)

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

@admin.register(MenuDia)
class MenuDiaAdmin(admin.ModelAdmin):
    list_display = ('fecha','publicado')
    inlines = [MenuItemInline]

class OrdenItemInline(admin.TabularInline):
    model = OrdenItem
    extra = 0

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('folio','estado','total','creado')
    list_filter = ('estado',)
    search_fields = ('folio',)
    inlines = [OrdenItemInline]

admin.site.register(Pago)
