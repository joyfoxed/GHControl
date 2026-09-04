"""Views do front-end do GHControl."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import MovimentacaoForm
from .models import HistoricoMovimentacao, ItemEstoque, Reagente


def inicio(request):
    """Rota raiz: redireciona para portal (logado) ou login (visitante)."""
    if request.user.is_authenticated:
        return redirect('estoque:portal')
    return redirect('estoque:login')


def login_view(request):
    """Tela de login personalizada do GHControl."""
    if request.user.is_authenticated:
        return redirect('estoque:portal')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('estoque:portal')

    return render(request, 'estoque/login.html', {'form': form})


@login_required
def portal(request):
    """Portal de escolha após autenticação (Dashboard ou Admin)."""
    return render(request, 'estoque/portal.html')


@login_required
def dashboard(request):
    """Painel inicial com métricas, alertas de validade e últimas movimentações."""
    hoje = timezone.localdate()
    limite_alerta = hoje + timedelta(days=30)

    itens_vencidos = (
        ItemEstoque.objects.filter(validade__lt=hoje)
        .select_related('reagente')
        .order_by('validade')
    )
    itens_alerta = (
        ItemEstoque.objects.filter(validade__gte=hoje, validade__lte=limite_alerta)
        .select_related('reagente')
        .order_by('validade')
    )

    total_vencidos = itens_vencidos.count()
    total_alerta = itens_alerta.count()
    total_validos = ItemEstoque.objects.filter(validade__gt=limite_alerta).count()

    # Gráfico 1: frascos por armário
    frascos_por_armario = (
        ItemEstoque.objects.values('armario__posicao')
        .annotate(total=Count('id'))
        .order_by('armario__posicao')
    )
    chart_armarios_labels = [
        f'Armário {item["armario__posicao"]}' for item in frascos_por_armario
    ]
    chart_armarios_data = [item['total'] for item in frascos_por_armario]

    # Gráfico 2: status de validade
    status_validade = {
        'labels': ['Vencidos', 'Em Alerta (30d)', 'Válidos'],
        'data': [total_vencidos, total_alerta, total_validos],
    }

    contexto = {
        'total_reagentes': Reagente.objects.count(),
        'total_frascos': ItemEstoque.objects.count(),
        'total_vencidos': total_vencidos,
        'total_alerta': total_alerta,
        'total_validos': total_validos,
        'itens_vencidos': itens_vencidos,
        'itens_alerta': itens_alerta,
        'chart_armarios_labels': chart_armarios_labels,
        'chart_armarios_data': chart_armarios_data,
        'status_validade': status_validade,
        'ultimas_movimentacoes': (
            HistoricoMovimentacao.objects.select_related(
                'item_estoque__reagente',
                'usuario',
            )[:5]
        ),
    }
    return render(request, 'estoque/dashboard.html', contexto)


@login_required
def lista_estoque(request):
    """Lista todos os frascos em estoque."""
    itens = (
        ItemEstoque.objects.select_related('reagente', 'armario')
        .prefetch_related('reagente__classificacoes_ghs')
        .order_by('reagente__nome', 'validade')
    )
    return render(request, 'estoque/lista_estoque.html', {'itens': itens})


@login_required
def relatorio_inventario(request):
    """Relatório formal de inventário para auditoria e impressão."""
    hoje = timezone.localdate()
    limite_alerta = hoje + timedelta(days=30)

    itens = (
        ItemEstoque.objects.select_related('reagente', 'armario')
        .order_by('armario__posicao', 'reagente__nome', 'validade')
    )

    itens_auditoria = []
    for item in itens:
        if item.validade < hoje:
            status = 'Vencido'
            status_cor = 'red'
        elif item.validade <= limite_alerta:
            status = 'Em alerta'
            status_cor = 'amber'
        else:
            status = 'Válido'
            status_cor = 'emerald'
        itens_auditoria.append({
            'item': item,
            'status': status,
            'status_cor': status_cor,
        })

    return render(
        request,
        'estoque/relatorio_inventario.html',
        {
            'itens_auditoria': itens_auditoria,
            'data_emissao': timezone.localtime(),
            'total_itens': len(itens_auditoria),
        },
    )


@login_required
def detalhe_item(request, pk):
    """Ficha detalhada de um frasco individual (ItemEstoque)."""
    item = get_object_or_404(
        ItemEstoque.objects.select_related('reagente', 'armario')
        .prefetch_related('reagente__classificacoes_ghs'),
        pk=pk,
    )
    return render(request, 'estoque/detalhe_item.html', {'item': item})


@login_required
def busca_codigo_barras(request):
    """Busca rápida por código de barras — simula leitura de bipador/QR."""
    codigo = request.GET.get('codigo', '').strip()

    if not codigo:
        messages.error(request, 'Digite ou bip um código de barras.')
        return redirect(request.META.get('HTTP_REFERER', reverse('estoque:dashboard')))

    item = ItemEstoque.objects.filter(codigo_barras=codigo).first()

    if item:
        return redirect('estoque:detalhe_item', pk=item.pk)

    messages.error(request, 'Código de barras não encontrado.')
    return redirect(request.META.get('HTTP_REFERER', reverse('estoque:dashboard')))


@login_required
def registrar_movimentacao(request):
    """Formulário para registrar entradas, saídas, consumos e descartes."""
    item_id = request.GET.get('item')
    tipo_inicial = request.GET.get('tipo', 'Consumo')

    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user
            try:
                movimentacao.save()
            except ValidationError as exc:
                if hasattr(exc, 'message_dict'):
                    for mensagens in exc.message_dict.values():
                        for mensagem in mensagens:
                            messages.error(request, mensagem)
                else:
                    for mensagem in exc.messages:
                        messages.error(request, mensagem)
            else:
                messages.success(
                    request,
                    f'Movimentação de {movimentacao.tipo} registrada com sucesso!',
                )
                return redirect('estoque:registrar_movimentacao')
    else:
        initial = {}
        if item_id:
            initial['item_estoque'] = item_id
            initial['tipo'] = tipo_inicial
        form = MovimentacaoForm(initial=initial)

    return render(
        request,
        'estoque/registrar_movimentacao.html',
        {'form': form},
    )
