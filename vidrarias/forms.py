"""Formulários do módulo Vidrarias."""

from django import forms

from .models import HistoricoMovimentacaoVidraria, Vidraria

SELECT_CLASS = (
    'relative z-30 block w-full cursor-pointer appearance-auto rounded-lg '
    'border border-slate-300 bg-white px-4 py-2.5 pr-10 text-slate-800 '
    'shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 '
    'focus:ring-blue-200'
)

INPUT_CLASS = (
    'w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 '
    'text-slate-800 shadow-sm focus:border-blue-500 focus:outline-none '
    'focus:ring-2 focus:ring-blue-200'
)

TEXTAREA_CLASS = (
    'w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 '
    'text-slate-800 shadow-sm focus:border-blue-500 focus:outline-none '
    'focus:ring-2 focus:ring-blue-200'
)


class VidrariaForm(forms.ModelForm):
    class Meta:
        model = Vidraria
        fields = (
            'nome',
            'tipo',
            'volume',
            'calibracao',
            'quantidade_estoque',
            'estoque_minimo',
        )
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Ex.: Béquer, Pipeta volumétrica',
            }),
            'tipo': forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_tipo'}),
            'volume': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Ex.: 250 mL',
            }),
            'calibracao': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'id': 'id_calibracao',
                'placeholder': 'Ex.: Classe A',
            }),
            'quantidade_estoque': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '0'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '0'}),
        }

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        calibracao = (cleaned.get('calibracao') or '').strip()

        if tipo == Vidraria.Tipo.VOLUMETRICA and not calibracao:
            self.add_error('calibracao', 'Informe a calibração para vidrarias volumétricas.')
        if tipo == Vidraria.Tipo.GRADUADA:
            cleaned['calibracao'] = None
        return cleaned


class MovimentacaoVidrariaForm(forms.Form):
    vidraria = forms.ModelChoiceField(
        queryset=Vidraria.objects.order_by('nome'),
        label='Vidraria',
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
    )
    tipo = forms.ChoiceField(
        choices=HistoricoMovimentacaoVidraria.TipoMovimentacao.choices,
        label='Tipo de movimentação',
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
    )
    quantidade = forms.IntegerField(
        min_value=1,
        label='Quantidade',
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '1'}),
    )
    observacao = forms.CharField(
        required=False,
        label='Observação / Justificativa',
        widget=forms.Textarea(attrs={
            'class': TEXTAREA_CLASS,
            'rows': 3,
            'placeholder': 'Ex.: Quebra durante aula prática da turma X',
        }),
    )
