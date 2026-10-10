"""Rotas do módulo Vidrarias."""

from django.urls import path

from . import views

app_name = 'vidrarias'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('lista/', views.lista_vidrarias, name='lista'),
    path('novo/', views.cadastrar_vidraria, name='cadastrar'),
    path('movimentacao/', views.movimentacao_vidraria, name='movimentacao'),
    path('<int:pk>/', views.detalhe_vidraria, name='detalhe'),
    path('<int:pk>/editar/', views.editar_vidraria, name='editar'),
    path('<int:pk>/excluir/', views.excluir_vidraria, name='excluir'),
]
