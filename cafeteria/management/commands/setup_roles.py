from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from cafeteria.models import Categoria, Producto, MenuDia, MenuItem, Orden, OrdenItem

def perms_for(model, actions=('view',)):
    ct = ContentType.objects.get_for_model(model)
    out = []
    for act in actions:
        codename = f'{act}_{model._meta.model_name}'
        try:
            out.append(Permission.objects.get(content_type=ct, codename=codename))
        except Permission.DoesNotExist:
            pass
    return out

class Command(BaseCommand):
    help = "Crea grupos y asigna permisos del módulo cafetería"

    def handle(self, *args, **kwargs):
        grupos = {
            # Alumno: solo lectura de catálogo/menú
            'Alumno': (
                perms_for(Categoria, ('view',)) +
                perms_for(Producto, ('view',)) +
                perms_for(MenuDia, ('view',)) +
                perms_for(MenuItem, ('view',))
            ),
            # Cajero: operar POS (crear/cambiar órdenes), ver catálogo
            'Cajero': (
                perms_for(Orden, ('add', 'change', 'view')) +
                perms_for(OrdenItem, ('add', 'change', 'delete', 'view')) +
                perms_for(Producto, ('view',)) +
                perms_for(Categoria, ('view',)) +
                perms_for(MenuDia, ('view',)) +
                perms_for(MenuItem, ('view',))
            ),
            # Cocinero: cambiar estado de órdenes, ver catálogo
            'Cocinero': (
                perms_for(Orden, ('change', 'view')) +
                perms_for(OrdenItem, ('view',)) +
                perms_for(Producto, ('view',)) +
                perms_for(MenuDia, ('view',)) +
                perms_for(MenuItem, ('view',))
            ),
            # Supervisor: administra catálogos y menús
            'Supervisor': (
                perms_for(Categoria, ('add','change','delete','view')) +
                perms_for(Producto, ('add','change','delete','view')) +
                perms_for(MenuDia, ('add','change','delete','view')) +
                perms_for(MenuItem, ('add','change','delete','view')) +
                perms_for(Orden, ('view',)) +
                perms_for(OrdenItem, ('view',))
            ),
        }

        for nombre, permisos in grupos.items():
            g, _ = Group.objects.get_or_create(name=nombre)
            g.permissions.set(permisos)
            self.stdout.write(self.style.SUCCESS(f'Grupo {nombre} listo ({len(permisos)} permisos)'))

        self.stdout.write(self.style.SUCCESS('Roles y permisos configurados.'))
