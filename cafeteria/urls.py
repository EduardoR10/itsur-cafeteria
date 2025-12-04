from django.urls import path, include
from . import views
from .api import router as api_router

urlpatterns = [
    path('', views.home, name='home'),

    # POS
    path('pos/', views.pos, name='pos'),
    path('pos/nueva/', views.pos_nueva_orden, name='pos_nueva'),
    path('pos/add-item/', views.pos_add_item, name='pos_add_item'),
    path('pos/del-item/<int:item_id>/', views.pos_eliminar_item, name='pos_del_item'),
    path('pos/cobrar/', views.pos_cobrar, name='pos_cobrar'),
    path('pos/enviar-cocina/', views.pos_enviar_cocina, name='pos_enviar_cocina'),

    # Cocina
    path('cocina/', views.kitchen, name='kitchen'),
    path('cocina/cambiar/<int:orden_id>/<str:nuevo_estado>/',
         views.kitchen_cambiar_estado, name='kitchen_cambiar_estado'),


    # API
    path('api/', include(api_router.urls)),

    path('catalogo/', views.catalogo, name='catalogo'),

     path('reportes/ordenes/', views.reporte_ordenes, name='reportes_ordenes'),

     path('register/', views.register, name='register'),
     
]

