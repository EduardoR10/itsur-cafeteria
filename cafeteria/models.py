from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    def __str__(self): return self.nombre

class MenuDia(models.Model):
    fecha = models.DateField(unique=True)
    publicado = models.BooleanField(default=False)
    productos = models.ManyToManyField(Producto, through='MenuItem', related_name='menus')
    def __str__(self): return f"Menú {self.fecha}"

class MenuItem(models.Model):
    menu = models.ForeignKey(MenuDia, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    destacado = models.BooleanField(default=False)
    class Meta:
        unique_together = (('menu','producto'),)

class Orden(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE_PAGO = "PENDIENTE_PAGO", "Pendiente de pago"
        PAGADA = "PAGADA", "Pagada"
        EN_COLA = "EN_COLA", "En cola"
        EN_PREPARACION = "EN_PREPARACION", "En preparación"
        LISTA = "LISTA", "Lista"
        ENTREGADA = "ENTREGADA", "Entregada"

    folio = models.CharField(max_length=20, unique=True)
    alumno = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes')
    creada_por = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='ordenes_creadas')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE_PAGO)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creado = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Orden {self.folio}"

class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

class Pago(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name='pago')
    metodo = models.CharField(max_length=10, choices=Metodo.choices)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    recibido_en = models.DateTimeField(default=timezone.now)
