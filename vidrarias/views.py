"""Views do módulo Vidrarias."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import staff_member_required
from .forms import MovimentacaoVidrariaForm, VidrariaForm
from .models import HistoricoMovimentacaoVidraria, Vidraria


@login_required
def dashboard(request):
    """Dashboard do módulo Vidrarias."""
    todas = Vidraria.objects.all()
    estoque_baixo_qs = todas.filter(
        quantidade_estoque__lte=F('estoque_minimo')
    ).order_by('quantidade_estoque')

    total_pecas = todas.aggregate(total=Sum('quantidade_estoque'))['total'] or 0
    graduadas = todas.filter(tipo=Vidraria.Tipo.GRADUADA)
    volumetricas = todas.filter(tipo=Vidraria.Tipo.VOLUMETRICA)

    quebras = HistoricoMovimentacaoVidraria.objects.filter(
        tipo=HistoricoMovimentacaoVidraria.TipoMovimentacao.SAIDA_QUEBRA,
    ).select_related('vidraria', 'usuario')[:8]

    ultimas = HistoricoMovimentacaoVidraria.objects.select_related(
        'vidraria', 'usuario'
    )[:8]

    return render(
        request,
        'vidrarias/dashboard_vidrarias.html',
        {
            'total_itens': todas.count(),
            'total_pecas': total_pecas,
            'itens_estoque_baixo': estoque_baixo_qs.count(),
            'lista_estoque_baixo': estoque_baixo_qs[:8],
            'graduadas': graduadas,
            'volumetricas': volumetricas,
            'quebras_recentes': quebras,
            'ultimas_movimentacoes': ultimas,
        },
    )


@login_required
def lista_vidrarias(request):
    itens = Vidraria.objects.all()
    return render(request, 'vidrarias/lista_vidrarias.html', {'itens': itens})


@login_required
def detalhe_vidraria(request, pk):
    item = get_object_or_404(Vidraria, pk=pk)
    historico = item.movimentacoes.select_related('usuario')[:15]
    return render(
        request,
        'vidrarias/detalhe_vidraria.html',
        {'item': item, 'historico': historico},
    )


@login_required
@staff_member_required
def cadastrar_vidraria(request):
    if request.method == 'POST':
        form = VidrariaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vidraria cadastrada com sucesso!')
            return redirect('vidrarias:lista')
    else:
        form = VidrariaForm()
    return render(
        request,
        'vidrarias/form_vidraria.html',
        {'form': form, 'titulo': 'Cadastrar Vidraria'},
    )


@login_required
@staff_member_required
def editar_vidraria(request, pk):
    item = get_object_or_404(Vidraria, pk=pk)
    if request.method == 'POST':
        form = VidrariaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vidraria atualizada com sucesso!')
            return redirect('vidrarias:detalhe', pk=item.pk)
    else:
        form = VidrariaForm(instance=item)
    return render(
        request,
        'vidrarias/form_vidraria.html',
        {'form': form, 'titulo': f'Editar — {item.nome}', 'item': item},
    )


@login_required
@staff_member_required
def excluir_vidraria(request, pk):
    item = get_object_or_404(Vidraria, pk=pk)
    if request.method == 'POST':
        nome = item.nome
        item.delete()
        messages.success(request, f'Vidraria "{nome}" excluída.')
        return redirect('vidrarias:lista')
    return render(request, 'vidrarias/confirmar_exclusao.html', {'item': item})


@login_required
@staff_member_required
def movimentacao_vidraria(request):
    """Entrada ou Saída/Quebra (somente staff)."""
    initial = {}
    vidraria_id = request.GET.get('vidraria')
    if vidraria_id:
        initial['vidraria'] = vidraria_id

    if request.method == 'POST':
        form = MovimentacaoVidrariaForm(request.POST)
        if form.is_valid():
            vidraria = form.cleaned_data['vidraria']
            tipo = form.cleaned_data['tipo']
            quantidade = form.cleaned_data['quantidade']
            observacao = form.cleaned_data.get('observacao', '')
            try:
                vidraria.aplicar_ajuste_estoque(quantidade, tipo)
                HistoricoMovimentacaoVidraria.objects.create(
                    vidraria=vidraria,
                    tipo=tipo,
                    quantidade=quantidade,
                    usuario=request.user,
                    observacao=observacao,
                )
            except ValidationError as exc:
                messages.error(
                    request,
                    exc.messages[0] if hasattr(exc, 'messages') else str(exc),
                )
            else:
                messages.success(
                    request,
                    f'{tipo} de {quantidade} peça(s) registrada para {vidraria.nome}. '
                    f'Estoque atual: {vidraria.quantidade_estoque}.',
                )
                return redirect('vidrarias:movimentacao')
    else:
        form = MovimentacaoVidrariaForm(initial=initial)

    ultimas = HistoricoMovimentacaoVidraria.objects.select_related(
        'vidraria', 'usuario'
    )[:10]
    return render(
        request,
        'vidrarias/movimentacao.html',
        {'form': form, 'ultimas': ultimas},
    )
