"""Admin do módulo EPI / EPC."""

from django.contrib import admin

from .models import EPC, EPI, HistoricoMovimentacaoEquipamento


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'ca',
        'validade',
        'estoque_disponivel',
        'estoque_minimo',
        'local_armazenado',
        'status',
    )
    list_filter = ('status', 'risco_controla')
    search_fields = ('nome', 'ca', 'fabricante')
    date_hierarchy = 'validade'


@admin.register(EPC)
class EPCAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'local',
        'tipo_risco',
        'data_ultima_inspecao',
        'data_proxima_inspecao',
        'status',
    )
    list_filter = ('status', 'tipo_risco')
    search_fields = ('nome', 'local', 'tipo_risco')
    readonly_fields = ('data_proxima_inspecao',)
    date_hierarchy = 'data_proxima_inspecao'


@admin.register(HistoricoMovimentacaoEquipamento)
class HistoricoMovimentacaoEquipamentoAdmin(admin.ModelAdmin):
    list_display = (
        'data_hora',
        'tipo_equipamento',
        'tipo',
        'epi',
        'epc',
        'quantidade',
        'usuario',
    )
    list_filter = ('tipo_equipamento', 'tipo', 'data_hora')
    search_fields = ('epi__nome', 'epc__nome', 'justificativa', 'usuario__username')
    readonly_fields = ('data_hora',)
    autocomplete_fields = ('epi', 'epc', 'usuario')
    date_hierarchy = 'data_hora'
