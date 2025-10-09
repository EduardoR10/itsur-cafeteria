from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from .models import MenuDia, Producto, Orden, OrdenItem
from .forms import BuscarProductoForm, AddItemForm
from .utils import generar_folio

def home(request):
    hoy = timezone.localdate()
    menu = MenuDia.objects.filter(fecha=hoy, publicado=True).first()
    return render(request, 'home.html', {'menu': menu, 'hoy': hoy})

# -------- POS ----------
@login_required
@permission_required('cafeteria.add_orden', raise_exception=True)
def pos(request):
    form = BuscarProductoForm(request.GET or None)
    productos = Producto.objects.filter(disponible=True).select_related('categoria').order_by('nombre')
    if form.is_valid() and form.cleaned_data.get('q'):
        q = form.cleaned_data['q']
        productos = productos.filter(nombre__icontains=q)
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    productos_page = paginator.get_page(page)

    # orden actual en sesión (simple para MVP)
    orden_id = request.session.get('orden_id')
    orden = Orden.objects.filter(pk=orden_id).first() if orden_id else None

    return render(request, 'pos.html', {
        'form': form,
        'productos': productos_page,
        'orden': orden
    })

@login_required
@permission_required('cafeteria.add_orden', raise_exception=True)
@transaction.atomic
def pos_nueva_orden(request):
    # crear folio secuencial simple por conteo del día
    hoy = timezone.localdate()
    conteo = Orden.objects.filter(creado__date=hoy).count() + 1
    folio = generar_folio(conteo)
    orden = Orden.objects.create(folio=folio, creada_por=request.user)
    request.session['orden_id'] = orden.id
    return redirect('pos')

@login_required
@permission_required('cafeteria.change_orden', raise_exception=True)
@transaction.atomic
def pos_add_item(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST requerido")
    form = AddItemForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Datos inválidos")

    orden_id = request.session.get('orden_id')
    if not orden_id:
        return HttpResponseBadRequest("No hay orden activa")
    orden = get_object_or_404(Orden, pk=orden_id)

    producto = get_object_or_404(Producto, pk=form.cleaned_data['producto_id'], disponible=True)
    cantidad = form.cleaned_data['cantidad']
    item, created = OrdenItem.objects.get_or_create(
        orden=orden, producto=producto,
        defaults={'cantidad': cantidad, 'precio_unitario': producto.precio, 'subtotal': 0}
    )
    if not created:
        item.cantidad += cantidad
        item.precio_unitario = producto.precio
        item.save()

    # devuelve fragmento parcial del carrito para htmx
    return render(request, 'partials/_carrito.html', {'orden': orden})

@login_required
@permission_required('cafeteria.change_orden', raise_exception=True)
@transaction.atomic
def pos_eliminar_item(request, item_id):
    orden_id = request.session.get('orden_id')
    orden = get_object_or_404(Orden, pk=orden_id)
    item = get_object_or_404(OrdenItem, pk=item_id, orden=orden)
    item.delete()
    return render(request, 'partials/_carrito.html', {'orden': orden})

@login_required
@permission_required('cafeteria.change_orden', raise_exception=True)
@transaction.atomic
def pos_cobrar(request):
    orden_id = request.session.get('orden_id')
    if not orden_id:
        return HttpResponseBadRequest("No hay orden activa")
    orden = get_object_or_404(Orden, pk=orden_id)
    if not orden.items.exists():
        return HttpResponseBadRequest("La orden no tiene productos")
    orden.estado = Orden.Estado.PAGADA
    orden.save()
    return render(request, 'partials/_acciones_pos.html', {'orden': orden})

@login_required
@permission_required('cafeteria.change_orden', raise_exception=True)
@transaction.atomic
def pos_enviar_cocina(request):
    orden_id = request.session.get('orden_id')
    orden = get_object_or_404(Orden, pk=orden_id)
    if orden.estado != Orden.Estado.PAGADA:
        return HttpResponseBadRequest("La orden debe estar PAGADA")
    orden.estado = Orden.Estado.EN_COLA
    orden.save()
    # limpiar sesión
    request.session.pop('orden_id', None)
    # regresar vista entera del POS sin orden activa
    return redirect('pos')

# -------- Cocina ----------
@login_required
@permission_required('cafeteria.change_orden', raise_exception=True)
def kitchen(request):
    estados = [Orden.Estado.EN_COLA, Orden.Estado.EN_PREPARACION, Orden.Estado.LISTA]
    ordenes = Orden.objects.filter(estado__in=estados).order_by('creado').prefetch_related('items__producto')
    return render(request, 'kitchen.html', {'ordenes': ordenes})

@login_required
@permission_required('cafeteria.change_orden', raise_exception=True)
@transaction.atomic
def kitchen_cambiar_estado(request, orden_id, nuevo_estado):
    orden = get_object_or_404(Orden, pk=orden_id)
    validos = {e for e, _ in Orden.Estado.choices}
    if nuevo_estado not in validos:
        return HttpResponseBadRequest("Estado inválido")
    orden.estado = nuevo_estado
    orden.save()
    # devolver tarjeta actualizada (htmx) o redirigir
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'partials/_card_orden.html', {'o': orden})
    return redirect('kitchen')
