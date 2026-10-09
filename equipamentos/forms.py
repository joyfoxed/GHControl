"""Formulários do módulo EPI / EPC."""

from django import forms
from django.utils import timezone

from .models import EPC, EPI

INPUT_CLASS = (
    'w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 '
    'text-slate-800 shadow-sm focus:border-emerald-500 focus:outline-none '
    'focus:ring-2 focus:ring-emerald-200'
)


class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = (
            'nome',
            'ca',
            'validade',
            'fabricante',
            'modelo',
            'estoque_disponivel',
            'estoque_minimo',
            'local_armazenado',
            'risco_controla',
            'status',
        )
        widgets = {
            field: forms.TextInput(attrs={'class': INPUT_CLASS})
            for field in (
                'nome',
                'ca',
                'fabricante',
                'modelo',
                'local_armazenado',
                'risco_controla',
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['validade'].widget = forms.DateInput(
            attrs={'class': INPUT_CLASS, 'type': 'date'},
            format='%Y-%m-%d',
        )
        self.fields['validade'].input_formats = ['%Y-%m-%d']
        self.fields['estoque_disponivel'].widget = forms.NumberInput(
            attrs={'class': INPUT_CLASS, 'min': '0'}
        )
        self.fields['estoque_minimo'].widget = forms.NumberInput(
            attrs={'class': INPUT_CLASS, 'min': '0'}
        )
        self.fields['status'].widget = forms.Select(attrs={'class': INPUT_CLASS})


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('nome', 'local', 'tipo_risco', 'observacoes'):
            self.fields[name].widget.attrs.update({'class': INPUT_CLASS})
        self.fields['frequencia_inspecao_dias'].widget = forms.NumberInput(
            attrs={'class': INPUT_CLASS, 'min': '1'}
        )
        self.fields['data_ultima_inspecao'].widget = forms.DateInput(
            attrs={'class': INPUT_CLASS, 'type': 'date'},
            format='%Y-%m-%d',
        )
        self.fields['data_ultima_inspecao'].input_formats = ['%Y-%m-%d']
        self.fields['status'].widget = forms.Select(attrs={'class': INPUT_CLASS})


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
