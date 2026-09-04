"""
Comando de carga de dados para apresentação do TCC — GHControl.

Popula usuários, armários, reagentes, frascos e histórico de entradas
com cenários realistas para demonstrar alertas de validade e o dashboard.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
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

# Posições reservadas para a apresentação (evita conflito com dados existentes).
ARMARIOS = {
    901: 'Armário A — Solventes',
    902: 'Armário B — Ácidos',
}

FRASCOS_APRESENTACAO = [
    {
        'reagente': 'Álcool Etílico',
        'cas': '64-17-5',
        'ghs': 'Inflamável',
        'armario': 901,
        'lote': 'ETOH-TCC-001',
        'validade_dias': -30,
        'quantidade': Decimal('1'),
        'unidade': 'L',
        'concentracao': Decimal('96'),
        'conc_unidade': '%',
        'fornecedor': 'SynthLab Química',
        'codigo_barras': '7891001',
        'justificativa': 'Entrada inicial — Álcool Etílico (apresentação TCC)',
    },
    {
        'reagente': 'Ácido Sulfúrico',
        'cas': '7664-93-9',
        'ghs': 'Corrosivo',
        'armario': 902,
        'lote': 'H2SO4-TCC-001',
        'validade_dias': 15,
        'quantidade': Decimal('500'),
        'unidade': 'mL',
        'concentracao': Decimal('98'),
        'conc_unidade': '%',
        'fornecedor': 'Merck Brasil',
        'codigo_barras': '7891002',
        'justificativa': 'Entrada inicial — Ácido Sulfúrico (apresentação TCC)',
    },
    {
        'reagente': 'Acetona',
        'cas': '67-64-1',
        'ghs': 'Inflamável',
        'armario': 901,
        'lote': 'ACE-TCC-001',
        'validade_dias': 365,
        'quantidade': Decimal('2'),
        'unidade': 'L',
        'concentracao': Decimal('99.5'),
        'conc_unidade': '%',
        'fornecedor': 'Neon Química',
        'codigo_barras': '7891003',
        'justificativa': 'Entrada inicial — Acetona (apresentação TCC)',
    },
]


class Command(BaseCommand):
    help = 'Popula o banco com dados realistas para a apresentação do TCC.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('GHControl — Carga de Apresentação TCC'))
        hoje = timezone.localdate()

        # --- Usuário técnico ---
        tecnico, criado = User.objects.get_or_create(username='tecnico_quimica')
        if criado:
            tecnico.set_password('senai123')
            tecnico.save()
            self.stdout.write(self.style.SUCCESS('  [OK] Usuario "tecnico_quimica" criado (senha: senai123)'))
        else:
            self.stdout.write('  • Usuario "tecnico_quimica" ja existia')

        # --- Armários ---
        armarios = {}
        for posicao, rotulo in ARMARIOS.items():
            armario, _ = Armario.objects.get_or_create(posicao=posicao)
            armarios[posicao] = armario
            self.stdout.write(f'  [OK] {rotulo} (posicao {posicao})')

        for dados in FRASCOS_APRESENTACAO:
            ghs = GHS.objects.get(nome=dados['ghs'])

            reagente, _ = Reagente.objects.get_or_create(
                cas=dados['cas'],
                defaults={'nome': dados['reagente']},
            )
            if reagente.nome != dados['reagente']:
                reagente.nome = dados['reagente']
                reagente.save(update_fields=['nome'])
            reagente.classificacoes_ghs.add(ghs)

            validade = hoje + timedelta(days=dados['validade_dias'])
            armario = armarios[dados['armario']]

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
                    'armario': armario,
                },
            )

            if not item_criado:
                item.validade = validade
                item.armario = armario
                item.codigo_barras = dados['codigo_barras']
                item.save()

            # Entrada inicial (atualiza o saldo via lógica do model).
            ja_tem_entrada = HistoricoMovimentacao.objects.filter(
                item_estoque=item,
                tipo=HistoricoMovimentacao.TipoMovimentacao.ENTRADA,
                justificativa=dados['justificativa'],
            ).exists()

            if not ja_tem_entrada:
                HistoricoMovimentacao.objects.create(
                    item_estoque=item,
                    tipo=HistoricoMovimentacao.TipoMovimentacao.ENTRADA,
                    quantidade=dados['quantidade'],
                    unidade=dados['unidade'],
                    usuario=tecnico,
                    justificativa=dados['justificativa'],
                )
            else:
                # Garante saldo correto em reexecuções sem duplicar histórico.
                item.quantidade = dados['quantidade']
                item.save(update_fields=['quantidade'])

            status_validade = (
                'VENCIDO' if validade < hoje
                else 'ALERTA 30d' if validade <= hoje + timedelta(days=30)
                else 'OK'
            )
            self.stdout.write(
                f'  [OK] {dados["reagente"]} — {dados["quantidade"]} {dados["unidade"]} '
                f'| Validade: {validade:%d/%m/%Y} [{status_validade}]'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Carga concluída com sucesso!'))
        self.stdout.write('')
        self.stdout.write('Credenciais para demonstração:')
        self.stdout.write('  Usuário: tecnico_quimica')
        self.stdout.write('  Senha:   senai123')
        self.stdout.write('')
        self.stdout.write('Códigos de barras para busca rápida:')
        for dados in FRASCOS_APRESENTACAO:
            self.stdout.write(f'  {dados["reagente"]}: {dados["codigo_barras"]}')