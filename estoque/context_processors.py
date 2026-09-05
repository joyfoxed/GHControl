"""Variáveis de permissão disponíveis em todos os templates."""

from .permissions import usuario_pode_movimentar_estoque


def permissoes_estoque(request):
    return {
        'pode_movimentar_estoque': usuario_pode_movimentar_estoque(request.user),
    }
