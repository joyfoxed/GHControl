"""Admin do módulo Vidrarias."""

from django.contrib import admin

from .models import HistoricoMovimentacaoVidraria, Vidraria


@admin.register(Vidraria)
class VidrariaAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'tipo',
        'volume',
        'calibracao',
        'quantidade_estoque',
        'estoque_minimo',
        'atualizado_em',
    )
    list_filter = ('tipo',)
    search_fields = ('nome', 'volume', 'calibracao')
    ordering = ('tipo', 'nome')


@admin.register(HistoricoMovimentacaoVidraria)
class HistoricoMovimentacaoVidrariaAdmin(admin.ModelAdmin):
    list_display = (
        'data_hora',
        'vidraria',
        'tipo',
        'quantidade',
        'usuario',
    )
    list_filter = ('tipo', 'data_hora')
    search_fields = ('vidraria__nome', 'observacao', 'usuario__username')
    readonly_fields = ('data_hora',)
    autocomplete_fields = ('vidraria', 'usuario')
    date_hierarchy = 'data_hora'
