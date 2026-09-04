"""Formulários do app estoque."""

from django import forms

from .models import HistoricoMovimentacao, ItemEstoque, normalizar_unidade

INPUT_CLASS = (
    'w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 '
    'text-slate-800 shadow-sm focus:border-emerald-500 focus:outline-none '
    'focus:ring-2 focus:ring-emerald-200'
)


class MovimentacaoForm(forms.ModelForm):
    """Formulário de registro de movimentação de estoque."""

    class Meta:
        model = HistoricoMovimentacao
        fields = ('item_estoque', 'tipo', 'quantidade', 'unidade', 'justificativa')
        widgets = {
            'item_estoque': forms.Select(attrs={'class': INPUT_CLASS}),
            'tipo': forms.Select(attrs={'class': INPUT_CLASS}),
            'quantidade': forms.NumberInput(
                attrs={
                    'class': INPUT_CLASS,
                    'step': '0.01',
                    'min': '0.01',
                }
            ),
            'unidade': forms.Select(attrs={'class': INPUT_CLASS}),
            'justificativa': forms.TextInput(
                attrs={
                    'class': INPUT_CLASS,
                    'placeholder': 'Ex.: Preparação de aula prática, reposição de lote...',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_estoque'].queryset = (
            self.fields['item_estoque']
            .queryset.select_related('reagente')
            .order_by('reagente__nome', 'lote')
        )
        self.fields['item_estoque'].label_from_instance = (
            lambda item: (
                f'{item.reagente.nome} — Lote {item.lote} '
                f'({item.quantidade} {item.qtd_unidade})'
            )
        )
        self.fields['unidade'].help_text = (
            'Informe a unidade usada na operação. O sistema converte automaticamente '
            'para a unidade do frasco (ex.: consumir 500 mL de um frasco em L).'
        )

        # Pré-seleciona a unidade do frasco quando o item já vem definido.
        item_id = self.initial.get('item_estoque') or self.data.get('item_estoque')
        if item_id and 'unidade' not in self.initial:
            try:
                item = ItemEstoque.objects.get(pk=item_id)
                unidade_normalizada = normalizar_unidade(item.qtd_unidade)
                if unidade_normalizada in dict(HistoricoMovimentacao.UnidadeMovimentacao.choices):
                    self.initial.setdefault('unidade', unidade_normalizada)
            except ItemEstoque.DoesNotExist:
                pass
