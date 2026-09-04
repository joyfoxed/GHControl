"""Rotas do app estoque."""

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('portal/', views.portal, name='portal'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estoque/', views.lista_estoque, name='lista_estoque'),
    path('estoque/relatorio/', views.relatorio_inventario, name='relatorio_inventario'),
    path('estoque/<int:pk>/', views.detalhe_item, name='detalhe_item'),
    path('busca/', views.busca_codigo_barras, name='busca_codigo_barras'),
    path('movimentacao/', views.registrar_movimentacao, name='registrar_movimentacao'),
]
