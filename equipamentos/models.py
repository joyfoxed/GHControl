"""
Modelos do módulo EPI / EPC — Equipamentos de Proteção Individual e Coletiva.

Sem ImageField/FileField: ambiente Serverless (Vercel) não persiste uploads locais.
"""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class EPI(models.Model):
    """Equipamento de Proteção Individual (ex.: luvas, óculos, jaleco)."""

    class Status(models.TextChoices):
        ATIVO = 'Ativo', 'Ativo'
        VENCIDO = 'Vencido', 'Vencido'
        BLOQUEADO = 'Bloqueado', 'Bloqueado'
        DESCONTINUADO = 'Descontinuado', 'Descontinuado'

    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do EPI',
        help_text='Descrição do equipamento de proteção individual.',
    )
    ca = models.CharField(
        max_length=50,
        verbose_name='CA — Certificado de Aprovação',
        help_text='Número do Certificado de Aprovação do MTE.',
    )
    validade = models.DateField(
        verbose_name='Data de validade',
        help_text='Validade do CA ou do lote do EPI.',
    )
    fabricante = models.CharField(max_length=200, verbose_name='Fabricante')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    estoque_disponivel = models.PositiveIntegerField(
        default=0,
        verbose_name='Estoque disponível',
        help_text='Quantidade de unidades disponíveis.',
    )
    estoque_minimo = models.PositiveIntegerField(
        default=1,
        verbose_name='Estoque mínimo',
        help_text='Quantidade mínima para alerta de reposição.',
    )
    local_armazenado = models.CharField(
        max_length=200,
        verbose_name='Local armazenado',
        help_text='Ex.: Armário de EPIs, Sala de segurança, Prateleira 2.',
    )
    risco_controla = models.CharField(
        max_length=200,
        verbose_name='Risco que controla',
        help_text='Ex.: Químico, Mecânico, Térmico, Biológico.',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO,
        verbose_name='Status',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'EPI'
        verbose_name_plural = 'EPIs'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} (CA: {self.ca})'

    @property
    def estoque_baixo(self):
        return self.estoque_disponivel <= self.estoque_minimo

    @property
    def validade_vencida(self):
        return self.validade < timezone.localdate()

    def clean(self):
        super().clean()
        if self.validade and self.validade < timezone.localdate():
            if self.status == self.Status.ATIVO:
                self.status = self.Status.VENCIDO

    def dar_baixa(self, quantidade):
        """Reduz o estoque disponível. Lança ValidationError se insuficiente."""
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')
        if quantidade > self.estoque_disponivel:
            raise ValidationError(
                f'Estoque insuficiente. Disponível: {self.estoque_disponivel} unidade(s).'
            )
        self.estoque_disponivel -= quantidade
        self.save(update_fields=['estoque_disponivel', 'atualizado_em'])


class EPC(models.Model):
    """Equipamento de Proteção Coletiva (ex.: chuveiro, lava-olhos, extintor)."""

    class Status(models.TextChoices):
        ATIVO = 'Ativo', 'Ativo'
        DESATIVADO = 'Desativado', 'Desativado'
        BLOQUEADO = 'Bloqueado', 'Bloqueado'
        MANUTENCAO = 'Manutenção', 'Manutenção'
        DESCONTINUADO = 'Descontinuado', 'Descontinuado'

    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do EPC',
        help_text='Descrição do equipamento de proteção coletiva.',
    )
    local = models.CharField(
        max_length=200,
        verbose_name='Local',
        help_text='Onde o EPC está instalado no laboratório.',
    )
    tipo_risco = models.CharField(
        max_length=200,
        verbose_name='Tipo de risco que protege',
        help_text='Ex.: Incêndio, Contaminação química, Queda.',
    )
    frequencia_inspecao_dias = models.PositiveIntegerField(
        default=30,
        verbose_name='Frequência de inspeção (dias)',
        help_text='Intervalo em dias entre inspeções periódicas.',
    )
    data_ultima_inspecao = models.DateField(
        verbose_name='Data da última inspeção',
        help_text='Data da inspeção mais recente.',
    )
    data_proxima_inspecao = models.DateField(
        verbose_name='Data da próxima inspeção',
        editable=False,
        help_text='Calculada automaticamente (última inspeção + frequência).',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO,
        verbose_name='Status',
    )
    observacoes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Observações',
        help_text='Anotações da última inspeção ou manutenção.',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'EPC'
        verbose_name_plural = 'EPCs'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} — {self.local}'

    @property
    def inspecao_atrasada(self):
        if not self.data_proxima_inspecao:
            return False
        return self.data_proxima_inspecao < timezone.localdate()

    @property
    def inspecao_proxima(self):
        """True se a próxima inspeção cai nos próximos 7 dias (e ainda não atrasou)."""
        if not self.data_proxima_inspecao:
            return False
        hoje = timezone.localdate()
        return hoje <= self.data_proxima_inspecao <= hoje + timedelta(days=7)

    def calcular_proxima_inspecao(self):
        if self.data_ultima_inspecao and self.frequencia_inspecao_dias:
            return self.data_ultima_inspecao + timedelta(days=self.frequencia_inspecao_dias)
        return None

    def save(self, *args, **kwargs):
        proxima = self.calcular_proxima_inspecao()
        if proxima:
            self.data_proxima_inspecao = proxima
        super().save(*args, **kwargs)

    def registrar_inspecao(self, data_inspecao=None, observacoes=''):
        """Registra inspeção e recalcula a próxima data automaticamente."""
        self.data_ultima_inspecao = data_inspecao or timezone.localdate()
        if observacoes:
            self.observacoes = observacoes
        if self.status == self.Status.MANUTENCAO:
            self.status = self.Status.ATIVO
        self.save()
