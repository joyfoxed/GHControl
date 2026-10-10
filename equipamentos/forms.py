"""Formulários do módulo EPI / EPC."""

from django import forms
from django.utils import timezone

from .models import EPC, EPI, HistoricoMovimentacaoEquipamento

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


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = (
            'nome',
            'ca',
            'validade',
            'fabricante',
            'estoque_disponivel',
            'estoque_minimo',
            'local_armazenado',
            'risco_controla',
            'status',
        )
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Ex.: Luva Nitrílica Azul M',
            }),
            'ca': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'fabricante': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'local_armazenado': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'risco_controla': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'validade': forms.DateInput(
                attrs={'class': INPUT_CLASS, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'estoque_disponivel': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '0'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['validade'].input_formats = ['%Y-%m-%d']
        self.fields['status'].choices = EPI.Status.choices


class EPCForm(forms.ModelForm):
    class Meta:
        model = EPC
        fields = (
            'nome',
            'local',
            'tipo_risco',
            'frequencia_inspecao_dias',
            'data_ultima_inspecao',
            'status',
            'observacoes',
        )
        widgets = {
            'nome': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'local': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'tipo_risco': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'observacoes': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'frequencia_inspecao_dias': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '1'}),
            'data_ultima_inspecao': forms.DateInput(
                attrs={'class': INPUT_CLASS, 'type': 'date'},
                format='%Y-%m-%d',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_ultima_inspecao'].input_formats = ['%Y-%m-%d']
        self.fields['status'].choices = EPC.Status.choices


class BaixaEPIForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        label='Quantidade a dar baixa',
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '1'}),
    )
    justificativa = forms.CharField(
        max_length=255,
        required=False,
        label='Justificativa (opcional)',
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Ex.: Entrega ao aluno da turma X',
            }
        ),
    )


class InspecaoEPCForm(forms.Form):
    data_inspecao = forms.DateField(
        label='Data da inspeção',
        initial=timezone.localdate,
        widget=forms.DateInput(
            attrs={'class': INPUT_CLASS, 'type': 'date'},
            format='%Y-%m-%d',
        ),
        input_formats=['%Y-%m-%d'],
    )
    observacoes = forms.CharField(
        max_length=255,
        required=False,
        label='Observações',
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Condição do equipamento, ações realizadas...',
            }
        ),
    )


class MovimentacaoEquipamentoForm(forms.Form):
    """Formulário unificado de movimentação EPI/EPC."""

    tipo_equipamento = forms.ChoiceField(
        choices=HistoricoMovimentacaoEquipamento.TipoEquipamento.choices,
        label='Tipo de equipamento',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_tipo_equipamento'}),
    )
    epi = forms.ModelChoiceField(
        queryset=EPI.objects.order_by('nome'),
        required=False,
        label='EPI',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_epi'}),
    )
    epc = forms.ModelChoiceField(
        queryset=EPC.objects.order_by('nome'),
        required=False,
        label='EPC',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_epc'}),
    )
    tipo = forms.ChoiceField(
        choices=HistoricoMovimentacaoEquipamento.TipoOperacao.choices,
        label='Tipo de operação',
        widget=forms.Select(attrs={'class': SELECT_CLASS, 'id': 'id_tipo'}),
    )
    quantidade = forms.IntegerField(
        required=False,
        min_value=1,
        label='Quantidade',
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': '1'}),
    )
    justificativa = forms.CharField(
        max_length=255,
        required=False,
        label='Justificativa / Observação',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS}),
    )

    def clean(self):
        cleaned = super().clean()
        tipo_eq = cleaned.get('tipo_equipamento')
        tipo = cleaned.get('tipo')
        epi = cleaned.get('epi')
        epc = cleaned.get('epc')
        quantidade = cleaned.get('quantidade')

        if tipo_eq == 'EPI':
            if not epi:
                self.add_error('epi', 'Selecione o EPI.')
            if tipo == 'Inspeção':
                self.add_error('tipo', 'Inspeção aplica-se apenas a EPCs.')
            if not quantidade:
                self.add_error('quantidade', 'Informe a quantidade.')
        elif tipo_eq == 'EPC':
            if not epc:
                self.add_error('epc', 'Selecione o EPC.')
            if tipo != 'Inspeção':
                self.add_error('tipo', 'Para EPC, use o tipo Inspeção.')

        return cleaned
