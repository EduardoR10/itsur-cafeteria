from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import OrdenItem, Orden

@receiver(pre_save, sender=OrdenItem)
def calcular_subtotal(sender, instance: OrdenItem, **kwargs):
    instance.subtotal = instance.cantidad * instance.precio_unitario

def _recalcular_total(orden: Orden):
    total = sum(i.subtotal for i in orden.items.all())
    Orden.objects.filter(pk=orden.pk).update(total=total)

@receiver(post_save, sender=OrdenItem)
def actualizar_total_al_guardar(sender, instance, **kwargs):
    _recalcular_total(instance.orden)

@receiver(post_delete, sender=OrdenItem)
def actualizar_total_al_borrar(sender, instance, **kwargs):
    _recalcular_total(instance.orden)
