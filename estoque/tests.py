from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Armario, ItemEstoque, Reagente


User = get_user_model()


class BuscaEstoqueTests(TestCase):
    """Cobertura de busca_estoque por tipo (nome, CAS, código de barras)."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='tecnico_teste',
            password='senha_segura_123',
        )
        self.client.login(username='tecnico_teste', password='senha_segura_123')

        self.armario = Armario.objects.create(posicao=1)
        self.validade = date.today() + timedelta(days=365)

        self.reagente_acido_a = Reagente.objects.create(
            nome='Ácido Clorídrico',
            cas='7647-01-0',
        )
        self.reagente_acido_b = Reagente.objects.create(
            nome='Ácido Sulfúrico',
            cas='7664-93-9',
        )
        self.reagente_agua = Reagente.objects.create(
            nome='Água Destilada',
            cas='7732-18-5',
        )
        self.reagente_etanol = Reagente.objects.create(
            nome='Etanol Absoluto',
            cas='64-17-5',
        )

        self.item_acido_a = self._criar_item(
            reagente=self.reagente_acido_a,
            lote='LOTE-ACIDO-A',
            codigo_barras='CB-ACIDO-001',
        )
        self.item_acido_b = self._criar_item(
            reagente=self.reagente_acido_b,
            lote='LOTE-ACIDO-B',
            codigo_barras='CB-ACIDO-002',
        )
        self.item_agua = self._criar_item(
            reagente=self.reagente_agua,
            lote='LOTE-AGUA-1',
            codigo_barras='CB-AGUA-001',
        )
        self.item_etanol = self._criar_item(
            reagente=self.reagente_etanol,
            lote='LOTE-ETANOL-1',
            codigo_barras='CB-ETANOL-001',
        )

        self.url_busca = reverse('estoque:busca_estoque')

    def _criar_item(self, *, reagente, lote, codigo_barras):
        return ItemEstoque.objects.create(
            reagente=reagente,
            lote=lote,
            validade=self.validade,
            quantidade=Decimal('500.00'),
            qtd_unidade='mL',
            concentracao=Decimal('1.0000'),
            conc_unidade='M',
            fornecedor='Fornecedor Teste',
            codigo_barras=codigo_barras,
            armario=self.armario,
        )

    def test_busca_por_nome_parcial_retorna_lista_com_busca_tipo_key(self):
        """tipo=nome usa correspondência parcial e expõe busca_tipo_key."""
        resposta = self.client.get(
            self.url_busca,
            {'q': 'Ácido', 'tipo': 'nome'},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'estoque/lista_estoque.html')
        self.assertEqual(resposta.context['busca_tipo_key'], 'nome')
        self.assertEqual(resposta.context['busca_termo'], 'Ácido')
        self.assertEqual(resposta.context['busca_tipo'], 'Nome do Reagente')

        ids_encontrados = {item.pk for item in resposta.context['itens']}
        self.assertEqual(ids_encontrados, {self.item_acido_a.pk, self.item_acido_b.pk})
        self.assertNotIn(self.item_agua.pk, ids_encontrados)

    def test_busca_por_cas_parcial_retorna_lista_com_busca_tipo_key(self):
        """tipo=cas usa correspondência parcial e expõe busca_tipo_key."""
        # Dois reagentes com CAS iniciando em "76" → múltiplos resultados
        resposta = self.client.get(
            self.url_busca,
            {'q': '76', 'tipo': 'cas'},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'estoque/lista_estoque.html')
        self.assertEqual(resposta.context['busca_tipo_key'], 'cas')
        self.assertEqual(resposta.context['busca_termo'], '76')
        self.assertEqual(resposta.context['busca_tipo'], 'CAS')

        ids_encontrados = {item.pk for item in resposta.context['itens']}
        self.assertEqual(ids_encontrados, {self.item_acido_a.pk, self.item_acido_b.pk})
        self.assertNotIn(self.item_agua.pk, ids_encontrados)

    def test_busca_por_codigo_barras_exato_redireciona_para_detalhe(self):
        """tipo=codigo_barras exige correspondência exata; 1 resultado → detalhe."""
        resposta = self.client.get(
            self.url_busca,
            {'q': 'CB-ETANOL-001', 'tipo': 'codigo_barras'},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(
            resposta.url,
            reverse('estoque:detalhe_item', kwargs={'pk': self.item_etanol.pk}),
        )

    def test_busca_codigo_barras_nao_aceita_parcial(self):
        """Código de barras é exato: substring não encontra o frasco."""
        resposta = self.client.get(
            self.url_busca,
            {'q': 'CB-ETANOL', 'tipo': 'codigo_barras'},
        )

        self.assertEqual(resposta.status_code, 302)
        mensagens = [str(m) for m in resposta.wsgi_request._messages]
        self.assertTrue(
            any('Nenhum frasco encontrado' in m for m in mensagens),
            msg=f'Mensagem de erro esperada não encontrada: {mensagens}',
        )

    def test_busca_sem_tipo_comporta_como_codigo_barras(self):
        """Sem parâmetro tipo, o default é codigo_barras (busca exata)."""
        resposta = self.client.get(
            self.url_busca,
            {'q': 'CB-AGUA-001'},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(
            resposta.url,
            reverse('estoque:detalhe_item', kwargs={'pk': self.item_agua.pk}),
        )

    def test_busca_sem_tipo_com_parcial_nao_encontra(self):
        """Default codigo_barras: termo parcial sem tipo também falha."""
        resposta = self.client.get(
            self.url_busca,
            {'q': 'CB-AGUA'},
        )

        self.assertEqual(resposta.status_code, 302)
        mensagens = [str(m) for m in resposta.wsgi_request._messages]
        self.assertTrue(
            any('Código de Barras' in m for m in mensagens),
            msg=f'Mensagem de código de barras esperada não encontrada: {mensagens}',
        )

    def test_busca_tipo_key_nome_em_multiplos_resultados(self):
        """Lista múltipla por nome inclui busca_tipo_key com a chave bruta 'nome'."""
        resposta = self.client.get(
            self.url_busca,
            {'q': 'Ácido', 'tipo': 'nome'},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(list(resposta.context['itens'])), 2)
        self.assertEqual(resposta.context['busca_tipo_key'], 'nome')

    def test_busca_tipo_key_cas_em_multiplos_resultados(self):
        """Lista múltipla por CAS inclui busca_tipo_key com a chave bruta 'cas'."""
        resposta = self.client.get(
            self.url_busca,
            {'q': '76', 'tipo': 'cas'},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(list(resposta.context['itens'])), 2)
        self.assertEqual(resposta.context['busca_tipo_key'], 'cas')
