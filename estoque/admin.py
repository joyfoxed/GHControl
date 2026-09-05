"""
Configuração do painel de administração do app estoque (GHControl).

Registra todos os modelos e define listagens, buscas e filtros
para facilitar o gerenciamento visual dos dados.
"""

from django.contrib import admin

from .models import Armario, GHS, HistoricoMovimentacao, ItemEstoque, Reagente
from .permissions import usuario_pode_movimentar_estoque


@admin.register(GHS)
class GHSAdmin(admin.ModelAdmin):
    """Administração das classificações GHS de perigo químico."""

    list_display = ('nome', 'picto')
    search_fields = ('nome',)


@admin.register(Armario)
class ArmarioAdmin(admin.ModelAdmin):
    """Administração das localizações físicas (armários/prateleiras)."""

    list_display = ('posicao',)
    search_fields = ('posicao',)


@admin.register(Reagente)
class ReagenteAdmin(admin.ModelAdmin):
    """Administração do catálogo geral de reagentes."""

    list_display = ('nome', 'cas', 'classificacoes_ghs_display', 'fds_url')
    search_fields = ('nome', 'cas', 'classificacoes_ghs__nome')
    list_filter = ('classificacoes_ghs',)
    filter_horizontal = ('classificacoes_ghs',)
    fields = ('nome', 'cas', 'classificacoes_ghs', 'fds_url')

    @admin.display(description='Classificações GHS')
    def classificacoes_ghs_display(self, obj):
        """Lista os pictogramas GHS associados ao reagente."""
        return ', '.join(obj.classificacoes_ghs.values_list('nome', flat=True))


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    """Administração dos frascos físicos individuais em estoque."""

    list_display = (
        'reagente',
        'lote',
        'validade',
        'quantidade_com_unidade',
        'concentracao_com_unidade',
        'armario',
    )
    search_fields = ('lote', 'codigo_barras', 'reagente__nome')
    list_filter = ('validade', 'armario', 'reagente')
    autocomplete_fields = ('reagente', 'armario')

    @admin.display(description='Quantidade')
    def quantidade_com_unidade(self, obj):
        """Exibe quantidade e unidade juntas (ex.: 500,00 ml)."""
        return f'{obj.quantidade} {obj.qtd_unidade}'

    @admin.display(description='Concentração')
    def concentracao_com_unidade(self, obj):
        """Exibe concentração e unidade juntas (ex.: 37,00 %)."""
        return f'{obj.concentracao} {obj.conc_unidade}'


@admin.register(HistoricoMovimentacao)
class HistoricoMovimentacaoAdmin(admin.ModelAdmin):
    """Administração do histórico de auditoria de movimentações."""

    list_display = (
        'data_hora',
        'tipo',
        'item_estoque',
        'quantidade',
        'unidade',
        'usuario',
        'justificativa',
    )
    list_filter = ('tipo', 'data_hora', 'usuario')
    search_fields = (
        'item_estoque__reagente__nome',
        'item_estoque__lote',
        'justificativa',
        'usuario__username',
    )
    readonly_fields = ('data_hora',)
    autocomplete_fields = ('item_estoque', 'usuario')
    date_hierarchy = 'data_hora'

    def has_add_permission(self, request):
        return usuario_pode_movimentar_estoque(request.user)

    def has_change_permission(self, request, obj=None):
        return usuario_pode_movimentar_estoque(request.user)

    def has_delete_permission(self, request, obj=None):
        return usuario_pode_movimentar_estoque(request.user)
