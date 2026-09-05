"""
Regras de autorização do GHControl (RBAC).

A movimentação de estoque é a única operação de escrita no front-end.
Cadastros de reagente, armário e frasco ficam no Django Admin e já
respeitam as permissões nativas de cada modelo.
"""

PERM_MOVIMENTAR_ESTOQUE = 'estoque.pode_movimentar_estoque'
PERM_ADD_HISTORICO = 'estoque.add_historicomovimentacao'

MENSAGEM_SEM_PERMISSAO = (
    'Acesso restrito: sua conta não possui permissão para movimentar o estoque. '
    'Alunos têm acesso somente leitura. Solicite ao responsável do laboratório '
    'caso precise registrar entradas, saídas, consumo ou descarte.'
)


def usuario_pode_movimentar_estoque(user):
    """
    Retorna True se o usuário autenticado pode alterar o estoque.

    Superusuários sempre passam. Técnicos/professores recebem a permissão
    customizada (ou a nativa de adicionar histórico) via Grupo no Admin.
    O grupo Alunos não deve ter nenhuma dessas permissões.
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return user.has_perm(PERM_MOVIMENTAR_ESTOQUE) or user.has_perm(PERM_ADD_HISTORICO)
