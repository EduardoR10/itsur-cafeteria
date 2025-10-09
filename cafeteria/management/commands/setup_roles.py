from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

class Command(BaseCommand):
    help = "Crea grupos: alumno, cajero, cocinero, supervisor con permisos básicos."

    def handle(self, *args, **options):
        grupos = ['alumno', 'cajero', 'cocinero', 'supervisor']
        for g in grupos:
            Group.objects.get_or_create(name=g)

        # Permisos mínimos
        Producto = apps.get_model('cafeteria','Producto')
        Orden = apps.get_model('cafeteria','Orden')

        perms = Permission.objects.filter(content_type__app_label='cafeteria')
        by_codename = {p.codename: p for p in perms}

        alumno = Group.objects.get(name='alumno')
        cajero = Group.objects.get(name='cajero')
        cocinero = Group.objects.get(name='cocinero')
        supervisor = Group.objects.get(name='supervisor')

        # Cajero: add/change Orden y OrdenItem, ver productos
        asignar = [
            'add_orden','change_orden','view_orden',
            'add_ordenitem','change_ordenitem','delete_ordenitem','view_ordenitem',
            'view_producto'
        ]
        cajero.permissions.set([by_codename[c] for c in asignar if c in by_codename])

        # Cocinero: change/view Orden
        cocinero.permissions.set([by_codename[c] for c in ['change_orden','view_orden'] if c in by_codename])

        # Supervisor: view todo
        supervisor.permissions.set([p for p in perms if p.codename.startswith('view_')])

        self.stdout.write(self.style.SUCCESS("Grupos y permisos configurados."))
