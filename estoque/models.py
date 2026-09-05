"""
Modelos de dados do GHControl — Controle de Estoque e Segurança Química.

Estrutura baseada no diagrama de banco de dados refinado:
- GHS: classificação de perigo (Globally Harmonized System)
- Armario: localização física (prateleira/armário)
- Reagente: catálogo geral de substâncias químicas
- ItemEstoque: frascos físicos individuais em estoque
- HistoricoMovimentacao: auditoria de entradas, saídas e consumo
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

# Pictogramas GHS monitorados pelo mapa de compatibilidade (protótipo).
GHS_EXPLOSIVO = 'Explosivo'
GHS_INFLAMAVEL = 'Inflamável'
GHS_COMBURENTE = 'Comburente'
GHS_CORROSIVO = 'Corrosivo'

MSG_UNIDADES_INCOMPATIVEIS = (
    'Unidades incompatíveis: Não é possível converter massa em volume '
    'diretamente sem a densidade.'
)


def normalizar_unidade(unidade):
    """Padroniza variações comuns de unidade (ex.: ml → mL)."""
    mapa = {'ml': 'mL', 'l': 'L', 'kg': 'kg', 'g': 'g', 'L': 'L', 'mL': 'mL'}
    return mapa.get(unidade, unidade)


def converter_quantidade(quantidade, unidade_movimentacao, unidade_frasco):
    """
    Converte a quantidade da movimentação para a unidade do frasco.

    Regras: mesma unidade (direto); L↔mL e kg↔g (fator 1000); demais pares → erro.
    """
    unidade_mov = normalizar_unidade(unidade_movimentacao)
    unidade_frasco = normalizar_unidade(unidade_frasco)
    quantidade = Decimal(quantidade)

    if unidade_mov == unidade_frasco:
        return quantidade

    if unidade_frasco == 'L' and unidade_mov == 'mL':
        return quantidade / Decimal('1000')

    if unidade_frasco == 'mL' and unidade_mov == 'L':
        return quantidade * Decimal('1000')

    if unidade_frasco == 'kg' and unidade_mov == 'g':
        return quantidade / Decimal('1000')

    if unidade_frasco == 'g' and unidade_mov == 'kg':
        return quantidade * Decimal('1000')

    raise ValidationError(MSG_UNIDADES_INCOMPATIVEIS)


class GHS(models.Model):
    """
    Classificação GHS (Sistema Globalmente Harmonizado) de perigos químicos.

    Cada registro representa um tipo de perigo (ex.: inflamável, corrosivo)
    e armazena o pictograma correspondente.
    """

    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Descrição do perigo GHS (ex.: Inflamável, Corrosivo).',
    )
    picto = models.CharField(
        max_length=255,
        verbose_name='Pictograma',
        help_text='Caminho ou nome do arquivo do pictograma GHS.',
    )

    class Meta:
        verbose_name = 'GHS'
        verbose_name_plural = 'GHS'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Armario(models.Model):
    """
    Localização física no laboratório.

    Identifica a prateleira ou armário onde os frascos são armazenados.
    """

    posicao = models.IntegerField(
        verbose_name='Posição',
        unique=True,
        help_text='Número ou identificação da prateleira ou armário.',
    )

    class Meta:
        verbose_name = 'Armário'
        verbose_name_plural = 'Armários'
        ordering = ['posicao']

    def __str__(self):
        return f'Armário {self.posicao}'


class Reagente(models.Model):
    """
    Catálogo geral de reagentes químicos.

    Representa a substância em nível conceitual (nome, CAS, classificações GHS).
    Um reagente pode ter múltiplos pictogramas simultaneamente (ex.: Inflamável e Corrosivo).
    Os frascos físicos individuais são registrados em ItemEstoque.
    """

    nome = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Nome do reagente químico.',
    )
    cas = models.CharField(
        max_length=50,
        verbose_name='CAS',
        help_text='Número CAS (Chemical Abstracts Service) da substância.',
    )
    classificacoes_ghs = models.ManyToManyField(
        GHS,
        related_name='reagentes',
        verbose_name='Classificações GHS',
        blank=True,
        help_text='Pictogramas GHS aplicáveis ao reagente (pode haver mais de um).',
    )
    fds_url = models.URLField(
        'Link da FDS/FISPQ',
        blank=True,
        null=True,
        help_text='URL do PDF da Ficha de Dados de Segurança (FDS/FISPQ) do fabricante.',
    )

    class Meta:
        verbose_name = 'Reagente'
        verbose_name_plural = 'Reagentes'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} (CAS: {self.cas})'


class ItemEstoque(models.Model):
    """
    Frasco físico individual em estoque.

    Cada registro representa um frasco real com lote, validade, quantidade,
    concentração e localização. Frascos do mesmo reagente podem ter
    concentrações distintas — por isso a concentração fica nesta tabela.

    Valida compatibilidade química no armário via clean() antes de salvar.
    """

    reagente = models.ForeignKey(
        Reagente,
        on_delete=models.PROTECT,
        related_name='itens_estoque',
        verbose_name='Reagente',
        help_text='Reagente do catálogo ao qual este frasco pertence.',
    )
    lote = models.CharField(
        max_length=100,
        verbose_name='Lote',
        help_text='Identificação do lote de fabricação.',
    )
    validade = models.DateField(
        verbose_name='Validade',
        help_text='Data de validade do frasco.',
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Quantidade',
        help_text='Volume ou massa disponível no frasco.',
    )
    qtd_unidade = models.CharField(
        max_length=20,
        verbose_name='Unidade da quantidade',
        help_text='Unidade de medida da quantidade (ex.: ml, g, L).',
    )
    concentracao = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name='Concentração',
        help_text='Concentração deste frasco específico.',
    )
    conc_unidade = models.CharField(
        max_length=20,
        verbose_name='Unidade da concentração',
        help_text='Unidade da concentração (ex.: %, M, N).',
    )
    fornecedor = models.CharField(
        max_length=200,
        verbose_name='Fornecedor',
        help_text='Nome do fornecedor do frasco.',
    )
    codigo_barras = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Código de barras',
        help_text='Código de barras do frasco, se houver.',
    )
    armario = models.ForeignKey(
        Armario,
        on_delete=models.PROTECT,
        related_name='itens_estoque',
        verbose_name='Armário',
        help_text='Localização física (prateleira/armário) do frasco.',
    )

    class Meta:
        verbose_name = 'Item de estoque'
        verbose_name_plural = 'Itens de estoque'
        ordering = ['reagente__nome', 'validade']

    def __str__(self):
        return (
            f'{self.reagente.nome} — Lote {self.lote} '
            f'({self.quantidade} {self.qtd_unidade})'
        )

    def _classificacoes_ghs_do_reagente(self):
        """Retorna o conjunto de nomes GHS do reagente vinculado ao frasco."""
        if not self.reagente_id:
            return set()
        return set(self.reagente.classificacoes_ghs.values_list('nome', flat=True))

    def _classificacoes_ghs_no_armario(self):
        """Retorna as classificações GHS dos demais frascos já alocados no armário."""
        if not self.armario_id:
            return set()

        outros_itens = (
            ItemEstoque.objects.filter(armario_id=self.armario_id)
            .exclude(pk=self.pk)
            .prefetch_related('reagente__classificacoes_ghs')
        )

        classificacoes = set()
        for item in outros_itens:
            classificacoes.update(
                item.reagente.classificacoes_ghs.values_list('nome', flat=True)
            )
        return classificacoes

    @staticmethod
    def _possui_par_incompativel(classificacoes_a, classificacoes_b, nome_a, nome_b):
        """Verifica incompatibilidade bidirecional entre duas classificações GHS."""
        return (nome_a in classificacoes_a and nome_b in classificacoes_b) or (
            nome_b in classificacoes_a and nome_a in classificacoes_b
        )

    def clean(self):
        """
        Mapa de compatibilidade química — regras de armazenamento seguro.

        Compara as classificações GHS do frasco atual com as dos demais
        frascos já presentes no mesmo armário.
        """
        super().clean()

        if not self.armario_id or not self.reagente_id:
            return

        classificacoes_atuais = self._classificacoes_ghs_do_reagente()
        classificacoes_existentes = self._classificacoes_ghs_no_armario()

        if not classificacoes_existentes:
            return

        # Regra 1: Explosivos não podem compartilhar armário com outros reagentes.
        if GHS_EXPLOSIVO in classificacoes_atuais:
            raise ValidationError(
                'Risco de Acidente: Produtos Explosivos devem ser armazenados '
                'isoladamente. Não é permitido guardá-los junto com outros '
                'reagentes no mesmo armário!'
            )

        if GHS_EXPLOSIVO in classificacoes_existentes:
            raise ValidationError(
                'Risco de Acidente: Este armário já contém produtos Explosivos. '
                'Não é permitido armazenar outros reagentes no mesmo local!'
            )

        # Regra 2: Inflamável × Comburente (bidirecional).
        if self._possui_par_incompativel(
            classificacoes_atuais,
            classificacoes_existentes,
            GHS_INFLAMAVEL,
            GHS_COMBURENTE,
        ):
            raise ValidationError(
                'Risco de Acidente: Não é permitido armazenar produtos '
                'Inflamáveis junto com Comburentes no mesmo armário!'
            )

        # Regra 3: Inflamável × Corrosivo (bidirecional).
        if self._possui_par_incompativel(
            classificacoes_atuais,
            classificacoes_existentes,
            GHS_INFLAMAVEL,
            GHS_CORROSIVO,
        ):
            raise ValidationError(
                'Risco de Acidente: Não é permitido armazenar produtos '
                'Inflamáveis junto com Corrosivos no mesmo armário!'
            )

    def save(self, *args, **kwargs):
        """Garante validação de compatibilidade antes de persistir no banco."""
        self.full_clean()
        super().save(*args, **kwargs)


class HistoricoMovimentacao(models.Model):
    """
    Registro de auditoria das movimentações de estoque.

    Cada entrada registra quem alterou o estoque, quando, quanto e por quê.
    """

    class TipoMovimentacao(models.TextChoices):
        ENTRADA = 'Entrada', 'Entrada'
        SAIDA = 'Saída', 'Saída'
        CONSUMO = 'Consumo', 'Consumo'
        DESCARTE = 'Descarte', 'Descarte'

    class UnidadeMovimentacao(models.TextChoices):
        LITRO = 'L', 'L (Litros)'
        MILILITRO = 'mL', 'mL (Mililitros)'
        QUILOGRAMA = 'kg', 'kg (Quilogramas)'
        GRAMA = 'g', 'g (Gramas)'

    item_estoque = models.ForeignKey(
        ItemEstoque,
        on_delete=models.CASCADE,
        related_name='historico_movimentacoes',
        verbose_name='Item de estoque',
        help_text='Frasco físico afetado pela movimentação.',
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimentacao.choices,
        verbose_name='Tipo',
        help_text='Natureza da movimentação (entrada, saída, consumo ou descarte).',
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Quantidade',
        help_text='Quantidade movimentada na operação.',
    )
    unidade = models.CharField(
        max_length=5,
        choices=UnidadeMovimentacao.choices,
        default=UnidadeMovimentacao.MILILITRO,
        verbose_name='Unidade',
        help_text='Unidade em que a quantidade foi informada (pode diferir da unidade do frasco).',
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data e hora',
        help_text='Momento em que a movimentação foi registrada.',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimentacoes_estoque',
        verbose_name='Usuário',
        help_text='Usuário responsável pela alteração.',
    )
    justificativa = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Justificativa',
        help_text='Observação opcional (ex.: Quebra de frasco, Preparação de aula prática).',
    )

    class Meta:
        verbose_name = 'Histórico de movimentação'
        verbose_name_plural = 'Históricos de movimentação'
        ordering = ['-data_hora']
        permissions = [
            (
                'pode_movimentar_estoque',
                'Pode registrar movimentações de estoque (entrada, saída, consumo e descarte)',
            ),
        ]

    def __str__(self):
        return (
            f'{self.tipo} — {self.item_estoque.reagente.nome} '
            f'({self.quantidade} {self.unidade}) em {self.data_hora:%d/%m/%Y %H:%M}'
        )

    def quantidade_convertida(self):
        """Retorna a quantidade da movimentação convertida para a unidade do frasco."""
        item = ItemEstoque.objects.filter(pk=self.item_estoque_id).values(
            'qtd_unidade'
        ).first()
        if not item:
            return Decimal(self.quantidade)
        return converter_quantidade(
            self.quantidade,
            self.unidade,
            item['qtd_unidade'],
        )

    def clean(self):
        """Valida quantidade, compatibilidade de unidades e saldo disponível."""
        super().clean()

        if not self.item_estoque_id or not self.quantidade:
            return

        if self.quantidade <= 0:
            raise ValidationError({'quantidade': 'A quantidade deve ser maior que zero.'})

        quantidade_no_frasco = self.quantidade_convertida()

        tipos_saida = (
            self.TipoMovimentacao.SAIDA,
            self.TipoMovimentacao.CONSUMO,
            self.TipoMovimentacao.DESCARTE,
        )

        if self.tipo in tipos_saida:
            quantidade_disponivel = ItemEstoque.objects.filter(
                pk=self.item_estoque_id
            ).values_list('quantidade', flat=True).first()

            if (
                quantidade_disponivel is not None
                and quantidade_no_frasco > quantidade_disponivel
            ):
                unidade_frasco = normalizar_unidade(
                    ItemEstoque.objects.filter(pk=self.item_estoque_id)
                    .values_list('qtd_unidade', flat=True)
                    .first()
                )
                raise ValidationError(
                    'Quantidade insuficiente em estoque. '
                    f'Disponível: {quantidade_disponivel} {unidade_frasco}. '
                    f'Solicitado: {self.quantidade} {self.unidade} '
                    f'(= {quantidade_no_frasco} {unidade_frasco} no frasco).'
                )

    def _atualizar_quantidade_estoque(self):
        """Aplica o impacto da movimentação no saldo do frasco (com conversão de unidade)."""
        item = ItemEstoque.objects.select_for_update().get(pk=self.item_estoque_id)
        quantidade_convertida = converter_quantidade(
            self.quantidade,
            self.unidade,
            item.qtd_unidade,
        )

        if self.tipo == self.TipoMovimentacao.ENTRADA:
            item.quantidade += quantidade_convertida
        elif self.tipo in (
            self.TipoMovimentacao.SAIDA,
            self.TipoMovimentacao.CONSUMO,
            self.TipoMovimentacao.DESCARTE,
        ):
            item.quantidade -= quantidade_convertida

        item.save(update_fields=['quantidade'])

    def save(self, *args, **kwargs):
        """
        Registra a movimentação e atualiza automaticamente o estoque do frasco.

        A lógica de estoque roda apenas na criação do registro, evitando
        duplicidade em edições futuras pelo admin.
        """
        self.full_clean()

        if self._state.adding:
            with transaction.atomic():
                self._atualizar_quantidade_estoque()
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
