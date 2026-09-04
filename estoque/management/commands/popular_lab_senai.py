"""
Carga de reagentes comuns de laboratório — Lab SENAI (protótipo GHControl).

Utiliza APENAS os 4 armários já cadastrados (posições 1–4), sem criar novos.
Distribui frascos respeitando compatibilidade GHS e simula um lab em operação.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from estoque.models import (
    Armario,
    GHS,
    HistoricoMovimentacao,
    ItemEstoque,
    Reagente,
)

User = get_user_model()

# Armário 1 = Solventes | 2 = Ácidos | 3 = Bases | 4 = Sais e oxidantes
FRASCOS_LAB = [
    # --- Armário 1: Solventes inflamáveis ---
    {
        'reagente': 'Álcool Etílico',
        'cas': '64-17-5',
        'ghs': ['Inflamável'],
        'armario': 1,
        'lote': 'ETOH-96-2024-A',
        'validade_dias': -35,
        'quantidade': Decimal('1.8'),
        'unidade': 'L',
        'concentracao': Decimal('96'),
        'conc_unidade': '%',
        'fornecedor': 'SynthLab Química',
        'codigo_barras': 'SENAI-001',
    },
    {
        'reagente': 'Álcool Etílico',
        'cas': '64-17-5',
        'ghs': ['Inflamável'],
        'armario': 1,
        'lote': 'ETOH-70-2025-B',
        'validade_dias': 20,
        'quantidade': Decimal('450'),
        'unidade': 'mL',
        'concentracao': Decimal('70'),
        'conc_unidade': '%',
        'fornecedor': 'Dinâmica Química',
        'codigo_barras': 'SENAI-002',
    },
    {
        'reagente': 'Acetona',
        'cas': '67-64-1',
        'ghs': ['Inflamável'],
        'armario': 1,
        'lote': 'ACE-2025-03',
        'validade_dias': 420,
        'quantidade': Decimal('1'),
        'unidade': 'L',
        'concentracao': Decimal('99.5'),
        'conc_unidade': '%',
        'fornecedor': 'Neon Química',
        'codigo_barras': 'SENAI-003',
    },
    {
        'reagente': 'Metanol',
        'cas': '67-56-1',
        'ghs': ['Inflamável'],
        'armario': 1,
        'lote': 'MET-2025-01',
        'validade_dias': 12,
        'quantidade': Decimal('380'),
        'unidade': 'mL',
        'concentracao': Decimal('99.8'),
        'conc_unidade': '%',
        'fornecedor': 'Quimis Indústria',
        'codigo_barras': 'SENAI-004',
    },
    {
        'reagente': 'Hexano',
        'cas': '110-54-3',
        'ghs': ['Inflamável'],
        'armario': 1,
        'lote': 'HEX-2023-09',
        'validade_dias': -60,
        'quantidade': Decimal('180'),
        'unidade': 'mL',
        'concentracao': Decimal('95'),
        'conc_unidade': '%',
        'fornecedor': 'Vetec Química',
        'codigo_barras': 'SENAI-005',
    },
    # --- Armário 2: Ácidos corrosivos ---
    {
        'reagente': 'Ácido Sulfúrico',
        'cas': '7664-93-9',
        'ghs': ['Corrosivo'],
        'armario': 2,
        'lote': 'H2SO4-2024-02',
        'validade_dias': -42,
        'quantidade': Decimal('420'),
        'unidade': 'mL',
        'concentracao': Decimal('98'),
        'conc_unidade': '%',
        'fornecedor': 'Merck Brasil',
        'codigo_barras': 'SENAI-006',
    },
    {
        'reagente': 'Ácido Clorídrico',
        'cas': '7647-01-0',
        'ghs': ['Corrosivo'],
        'armario': 2,
        'lote': 'HCL-37-2025-A',
        'validade_dias': 18,
        'quantidade': Decimal('850'),
        'unidade': 'mL',
        'concentracao': Decimal('37'),
        'conc_unidade': '%',
        'fornecedor': 'Dinâmica Química',
        'codigo_barras': 'SENAI-007',
    },
    {
        'reagente': 'Ácido Clorídrico',
        'cas': '7647-01-0',
        'ghs': ['Corrosivo'],
        'armario': 2,
        'lote': 'HCL-10-2025-B',
        'validade_dias': 310,
        'quantidade': Decimal('200'),
        'unidade': 'mL',
        'concentracao': Decimal('10'),
        'conc_unidade': '%',
        'fornecedor': 'LabSynth Produtos',
        'codigo_barras': 'SENAI-008',
    },
    {
        'reagente': 'Ácido Nítrico',
        'cas': '7697-37-2',
        'ghs': ['Corrosivo', 'Comburente'],
        'armario': 2,
        'lote': 'HNO3-2025-01',
        'validade_dias': 280,
        'quantidade': Decimal('250'),
        'unidade': 'mL',
        'concentracao': Decimal('65'),
        'conc_unidade': '%',
        'fornecedor': 'Cromato Química',
        'codigo_barras': 'SENAI-009',
    },
    {
        'reagente': 'Ácido Acético',
        'cas': '64-19-7',
        'ghs': ['Corrosivo'],
        'armario': 2,
        'lote': 'CH3COOH-2025',
        'validade_dias': 90,
        'quantidade': Decimal('500'),
        'unidade': 'mL',
        'concentracao': Decimal('5'),
        'conc_unidade': '%',
        'fornecedor': 'Exodo Científica',
        'codigo_barras': 'SENAI-010',
    },
    # --- Armário 3: Bases e neutralizantes ---
    {
        'reagente': 'Hidróxido de Sódio',
        'cas': '1310-73-2',
        'ghs': ['Corrosivo'],
        'armario': 3,
        'lote': 'NAOH-2024-ESC',
        'validade_dias': -22,
        'quantidade': Decimal('420'),
        'unidade': 'g',
        'concentracao': Decimal('97'),
        'conc_unidade': '%',
        'fornecedor': 'Exodo Científica',
        'codigo_barras': 'SENAI-011',
    },
    {
        'reagente': 'Hidróxido de Potássio',
        'cas': '1310-58-3',
        'ghs': ['Corrosivo'],
        'armario': 3,
        'lote': 'KOH-2025-01',
        'validade_dias': 8,
        'quantidade': Decimal('230'),
        'unidade': 'g',
        'concentracao': Decimal('85'),
        'conc_unidade': '%',
        'fornecedor': 'Sigma-Aldrich Brasil',
        'codigo_barras': 'SENAI-012',
    },
    {
        'reagente': 'Hidróxido de Amônio',
        'cas': '1336-21-6',
        'ghs': ['Corrosivo', 'Irritante/Perigoso à camada de ozônio (Exclamação)'],
        'armario': 3,
        'lote': 'NH4OH-2025-02',
        'validade_dias': 24,
        'quantidade': Decimal('480'),
        'unidade': 'mL',
        'concentracao': Decimal('25'),
        'conc_unidade': '%',
        'fornecedor': 'LabSynth Produtos',
        'codigo_barras': 'SENAI-013',
    },
    {
        'reagente': 'Carbonato de Sódio',
        'cas': '497-19-8',
        'ghs': ['Irritante/Perigoso à camada de ozônio (Exclamação)'],
        'armario': 3,
        'lote': 'NA2CO3-2025',
        'validade_dias': 540,
        'quantidade': Decimal('950'),
        'unidade': 'g',
        'concentracao': Decimal('100'),
        'conc_unidade': '%',
        'fornecedor': 'Dinâmica Química',
        'codigo_barras': 'SENAI-014',
    },
    # --- Armário 4: Sais, oxidantes e indicadores ---
    {
        'reagente': 'Permanganato de Potássio',
        'cas': '7722-64-7',
        'ghs': ['Comburente', 'Toxicidade aguda (Caveira)'],
        'armario': 4,
        'lote': 'KMnO4-2025',
        'validade_dias': 480,
        'quantidade': Decimal('85'),
        'unidade': 'g',
        'concentracao': Decimal('99'),
        'conc_unidade': '%',
        'fornecedor': 'Vetec Química',
        'codigo_barras': 'SENAI-015',
    },
    {
        'reagente': 'Cloreto de Sódio',
        'cas': '7647-14-5',
        'ghs': [],
        'armario': 4,
        'lote': 'NACL-2025-PA',
        'validade_dias': 730,
        'quantidade': Decimal('1'),
        'unidade': 'kg',
        'concentracao': Decimal('100'),
        'conc_unidade': '%',
        'fornecedor': 'Neon Química',
        'codigo_barras': 'SENAI-016',
    },
    {
        'reagente': 'Sulfato de Cobre (II) pentahidratado',
        'cas': '7758-99-8',
        'ghs': [
            'Irritante/Perigoso à camada de ozônio (Exclamação)',
            'Perigoso ao meio ambiente (Aquático)',
        ],
        'armario': 4,
        'lote': 'CUSO4-2024-11',
        'validade_dias': 26,
        'quantidade': Decimal('210'),
        'unidade': 'g',
        'concentracao': Decimal('100'),
        'conc_unidade': '%',
        'fornecedor': 'Quimis Indústria',
        'codigo_barras': 'SENAI-017',
    },
    {
        'reagente': 'Fenolftaleína',
        'cas': '77-09-8',
        'ghs': ['Irritante/Perigoso à camada de ozônio (Exclamação)'],
        'armario': 4,
        'lote': 'FEN-2023-04',
        'validade_dias': -48,
        'quantidade': Decimal('18'),
        'unidade': 'g',
        'concentracao': Decimal('1'),
        'conc_unidade': '%',
        'fornecedor': 'Merck Brasil',
        'codigo_barras': 'SENAI-018',
    },
    {
        'reagente': 'Nitrato de Prata',
        'cas': '7761-88-8',
        'ghs': ['Corrosivo', 'Comburente'],
        'armario': 4,
        'lote': 'AGNO3-2025',
        'validade_dias': 360,
        'quantidade': Decimal('42'),
        'unidade': 'g',
        'concentracao': Decimal('100'),
        'conc_unidade': '%',
        'fornecedor': 'Cromato Química',
        'codigo_barras': 'SENAI-019',
    },
    {
        'reagente': 'Peróxido de Hidrogênio',
        'cas': '7722-84-1',
        'ghs': ['Comburente', 'Irritante/Perigoso à camada de ozônio (Exclamação)'],
        'armario': 4,
        'lote': 'H2O2-3PCT-2025',
        'validade_dias': 15,
        'quantidade': Decimal('350'),
        'unidade': 'mL',
        'concentracao': Decimal('3'),
        'conc_unidade': '%',
        'fornecedor': 'SynthLab Química',
        'codigo_barras': 'SENAI-020',
    },
]

JUSTIFICATIVA_PREFIXO = 'Carga lab SENAI — entrada inicial'


class Command(BaseCommand):
    help = (
        'Popula o lab SENAI com reagentes comuns usando os 4 armários existentes '
        '(sem criar novos armários).'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('GHControl — Carga Lab SENAI'))
        hoje = timezone.localdate()

        armarios = {
            a.posicao: a for a in Armario.objects.order_by('posicao')
        }
        if not armarios:
            raise CommandError(
                'Nenhum armário encontrado. Cadastre os 4 armários antes de rodar este comando.'
            )

        posicoes = sorted(armarios.keys())
        self.stdout.write(f'Armários utilizados: {posicoes} (total: {len(posicoes)})')
        self.stdout.write('')

        tecnico, _ = User.objects.get_or_create(username='tecnico_quimica')
        if not tecnico.has_usable_password():
            tecnico.set_password('senai123')
            tecnico.save()

        vencidos = alerta = validos = 0

        for dados in FRASCOS_LAB:
            posicao = dados['armario']
            if posicao not in armarios:
                raise CommandError(
                    f'Armário {posicao} não existe. Armários disponíveis: {posicoes}'
                )

            reagente, _ = Reagente.objects.get_or_create(
                cas=dados['cas'],
                defaults={'nome': dados['reagente']},
            )
            if reagente.nome != dados['reagente']:
                reagente.nome = dados['reagente']
                reagente.save(update_fields=['nome'])

            for nome_ghs in dados['ghs']:
                ghs = GHS.objects.get(nome=nome_ghs)
                reagente.classificacoes_ghs.add(ghs)

            validade = hoje + timedelta(days=dados['validade_dias'])
            justificativa = f'{JUSTIFICATIVA_PREFIXO}: {dados["reagente"]}'

            item, item_criado = ItemEstoque.objects.get_or_create(
                lote=dados['lote'],
                reagente=reagente,
                defaults={
                    'validade': validade,
                    'quantidade': Decimal('0'),
                    'qtd_unidade': dados['unidade'],
                    'concentracao': dados['concentracao'],
                    'conc_unidade': dados['conc_unidade'],
                    'fornecedor': dados['fornecedor'],
                    'codigo_barras': dados['codigo_barras'],
                    'armario': armarios[posicao],
                },
            )

            if not item_criado:
                item.validade = validade
                item.armario = armarios[posicao]
                item.fornecedor = dados['fornecedor']
                item.codigo_barras = dados['codigo_barras']
                item.save()

            ja_tem_entrada = HistoricoMovimentacao.objects.filter(
                item_estoque=item,
                tipo=HistoricoMovimentacao.TipoMovimentacao.ENTRADA,
                justificativa=justificativa,
            ).exists()

            if not ja_tem_entrada:
                HistoricoMovimentacao.objects.create(
                    item_estoque=item,
                    tipo=HistoricoMovimentacao.TipoMovimentacao.ENTRADA,
                    quantidade=dados['quantidade'],
                    unidade=dados['unidade'],
                    usuario=tecnico,
                    justificativa=justificativa,
                )
            else:
                item.quantidade = dados['quantidade']
                item.save(update_fields=['quantidade'])

            if validade < hoje:
                status = 'VENCIDO'
                vencidos += 1
            elif validade <= hoje + timedelta(days=30):
                status = 'ALERTA 30d'
                alerta += 1
            else:
                status = 'OK'
                validos += 1

            self.stdout.write(
                f'  [OK] Arm.{posicao} | {dados["reagente"]} '
                f'({dados["concentracao"]} {dados["conc_unidade"]}) — '
                f'{dados["quantidade"]} {dados["unidade"]} | '
                f'{dados["fornecedor"]} | Val: {validade:%d/%m/%Y} [{status}]'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Carga do laboratório SENAI concluída!'))
        self.stdout.write('')
        self.stdout.write('Resumo:')
        self.stdout.write(f'  Reagentes (catálogo): {Reagente.objects.count()}')
        self.stdout.write(f'  Frascos em estoque:  {ItemEstoque.objects.count()}')
        self.stdout.write(f'  Vencidos:            {vencidos}')
        self.stdout.write(f'  Em alerta (30d):     {alerta}')
        self.stdout.write(f'  Validos:             {validos}')
        self.stdout.write('')
        self.stdout.write('Distribuição por armário:')
        for pos in posicoes:
            qtd = ItemEstoque.objects.filter(armario__posicao=pos).count()
            self.stdout.write(f'  Armário {pos}: {qtd} frasco(s)')
        self.stdout.write('')
        self.stdout.write('Busca rápida (códigos de barras):')
        for dados in FRASCOS_LAB:
            self.stdout.write(f'  {dados["codigo_barras"]} — {dados["reagente"]}')
