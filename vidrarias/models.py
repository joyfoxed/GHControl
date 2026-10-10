"""
Modelos do módulo Vidrarias — materiais de vidro do laboratório.

Sem ImageField/FileField: ambiente Serverless (Vercel) não persiste uploads locais.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Vidraria(models.Model):
    """Peça de vidraria laboratorial (béquer, pipeta, balão, etc.)."""

    class Tipo(models.TextChoices):
        GRADUADA = 'Graduada', 'Graduada'
        VOLUMETRICA = 'Volumétrica', 'Volumétrica'

    nome = models.CharField(max_length=200, verbose_name='Nome')
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        verbose_name='Tipo',
    )
    volume = models.CharField(
        max_length=50,
        verbose_name='Volume',
        help_text='Ex.: 250 mL, 1000 mL, 10 mL.',
    )
    calibracao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Calibração',
        help_text='Aplicável a volumétricas (ex.: Classe A, ±0,03 mL).',
    )
    quantidade_estoque = models.PositiveIntegerField(
        default=0,
        verbose_name='Quantidade em estoque',
    )
    estoque_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name='Estoque mínimo',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vidraria'
        verbose_name_plural = 'Vidrarias'
        ordering = ['tipo', 'nome']

    def __str__(self):
        return f'{self.nome} ({self.volume}) — {self.tipo}'

    @property
    def estoque_baixo(self):
        return self.quantidade_estoque <= self.estoque_minimo

    def clean(self):
        super().clean()
        if self.tipo == self.Tipo.VOLUMETRICA and not (self.calibracao or '').strip():
            raise ValidationError({
                'calibracao': 'Informe a calibração para vidrarias volumétricas.',
            })
        if self.tipo == self.Tipo.GRADUADA:
            self.calibracao = None

    def aplicar_ajuste_estoque(self, quantidade, tipo_movimentacao):
        """Aplica entrada (+) ou saída/quebra (-) no estoque."""
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')

        saidas = {
            HistoricoMovimentacaoVidraria.TipoMovimentacao.SAIDA_QUEBRA,
        }

        if tipo_movimentacao in saidas:
            if quantidade > self.quantidade_estoque:
                raise ValidationError(
                    f'Estoque insuficiente. Disponível: {self.quantidade_estoque} peça(s).'
                )
            self.quantidade_estoque -= quantidade
        elif tipo_movimentacao == HistoricoMovimentacaoVidraria.TipoMovimentacao.ENTRADA:
            self.quantidade_estoque += quantidade
        else:
            raise ValidationError('Tipo de movimentação inválido.')

        self.save(update_fields=['quantidade_estoque', 'atualizado_em'])


class HistoricoMovimentacaoVidraria(models.Model):
    """Auditoria de entradas e saídas/quebras de vidrarias."""

    class TipoMovimentacao(models.TextChoices):
        ENTRADA = 'Entrada', 'Entrada'
        SAIDA_QUEBRA = 'Saída/Quebra', 'Saída/Quebra'

    vidraria = models.ForeignKey(
        Vidraria,
        on_delete=models.CASCADE,
        related_name='movimentacoes',
        verbose_name='Vidraria',
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimentacao.choices,
        verbose_name='Tipo de movimentação',
    )
    quantidade = models.PositiveIntegerField(verbose_name='Quantidade')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimentacoes_vidrarias',
        verbose_name='Usuário responsável',
    )
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data e hora')
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação / Justificativa',
        help_text='Ideal para registrar motivos de quebra.',
    )

    class Meta:
        verbose_name = 'Histórico de movimentação (Vidraria)'
        verbose_name_plural = 'Históricos de movimentação (Vidrarias)'
        ordering = ['-data_hora']

    def __str__(self):
        return (
            f'{self.tipo} — {self.vidraria.nome} '
            f'({self.quantidade}) em {self.data_hora:%d/%m/%Y %H:%M}'
        )
