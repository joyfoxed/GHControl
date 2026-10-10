"""Rotas do módulo EPI / EPC."""

from django.urls import path

from . import views

app_name = 'equipamentos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('movimentacao/', views.movimentacao_equipamento, name='movimentacao'),
    # EPI
    path('epi/', views.lista_epis, name='lista_epis'),
    path('epi/novo/', views.cadastrar_epi, name='cadastrar_epi'),
    path('epi/<int:pk>/', views.detalhe_epi, name='detalhe_epi'),
    path('epi/<int:pk>/editar/', views.editar_epi, name='editar_epi'),
    path('epi/<int:pk>/baixa/', views.dar_baixa_epi, name='dar_baixa_epi'),
    # EPC
    path('epc/', views.lista_epcs, name='lista_epcs'),
    path('epc/novo/', views.cadastrar_epc, name='cadastrar_epc'),
    path('epc/<int:pk>/', views.detalhe_epc, name='detalhe_epc'),
    path('epc/<int:pk>/editar/', views.editar_epc, name='editar_epc'),
    path('epc/<int:pk>/inspecao/', views.registrar_inspecao_epc, name='registrar_inspecao_epc'),
]
