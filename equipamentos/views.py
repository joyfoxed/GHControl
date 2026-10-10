"""Views do módulo EPI / EPC."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import requer_staff
from .forms import (
    BaixaEPIForm,
    EPCForm,
    EPIForm,
    InspecaoEPCForm,
    MovimentacaoEquipamentoForm,
)
from .models import EPC, EPI, HistoricoMovimentacaoEquipamento


@login_required
def dashboard(request):
    """Dashboard exclusivo do módulo EPI / EPC."""
    hoje = timezone.localdate()
    limite_inspecao = hoje + timedelta(days=7)

    epis_estoque_baixo_qs = EPI.objects.filter(
        estoque_disponivel__lte=F('estoque_minimo')
    ).order_by('estoque_disponivel')

    epcs_atrasados = EPC.objects.filter(
        data_proxima_inspecao__lt=hoje,
        status=EPC.Status.ATIVO,
    ).order_by('data_proxima_inspecao')

    epcs_proximos = EPC.objects.filter(
        data_proxima_inspecao__gte=hoje,
        data_proxima_inspecao__lte=limite_inspecao,
        status=EPC.Status.ATIVO,
    ).order_by('data_proxima_inspecao')

    contexto = {
        'total_epis': EPI.objects.count(),
        'total_epcs': EPC.objects.count(),
        'epis_estoque_baixo': epis_estoque_baixo_qs.count(),
        'epcs_inspecao_alerta': epcs_atrasados.count() + epcs_proximos.count(),
        'lista_epis_baixo': epis_estoque_baixo_qs[:8],
        'lista_epcs_atrasados': epcs_atrasados[:8],
        'lista_epcs_proximos': epcs_proximos[:8],
        'ultimos_epis': EPI.objects.order_by('-atualizado_em')[:5],
        'ultimos_epcs': EPC.objects.order_by('-atualizado_em')[:5],
        'ultimas_movimentacoes': (
            HistoricoMovimentacaoEquipamento.objects.select_related(
                'epi', 'epc', 'usuario'
            )[:5]
        ),
    }
    return render(request, 'equipamentos/dashboard_equipamentos.html', contexto)


@login_required
def lista_epis(request):
    itens = EPI.objects.all()
    return render(request, 'equipamentos/lista_epis.html', {'itens': itens})


@login_required
def detalhe_epi(request, pk):
    item = get_object_or_404(EPI, pk=pk)
    historico = item.movimentacoes.select_related('usuario')[:10]
    return render(
        request,
        'equipamentos/detalhe_epi.html',
        {'item': item, 'historico': historico},
    )


@login_required
@requer_staff
def cadastrar_epi(request):
    if request.method == 'POST':
        form = EPIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'EPI cadastrado com sucesso!')
            return redirect('equipamentos:lista_epis')
    else:
        form = EPIForm()
    return render(
        request,
        'equipamentos/form_epi.html',
        {'form': form, 'titulo': 'Cadastrar EPI'},
    )


@login_required
@requer_staff
def editar_epi(request, pk):
    item = get_object_or_404(EPI, pk=pk)
    if request.method == 'POST':
        form = EPIForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'EPI atualizado com sucesso!')
            return redirect('equipamentos:detalhe_epi', pk=item.pk)
    else:
        form = EPIForm(instance=item)
    return render(
        request,
        'equipamentos/form_epi.html',
        {'form': form, 'titulo': f'Editar EPI — {item.nome}', 'item': item},
    )


@login_required
@requer_staff
def dar_baixa_epi(request, pk):
    item = get_object_or_404(EPI, pk=pk)
    if request.method == 'POST':
        form = BaixaEPIForm(request.POST)
        if form.is_valid():
            quantidade = form.cleaned_data['quantidade']
            try:
                item.dar_baixa(quantidade)
                HistoricoMovimentacaoEquipamento.objects.create(
                    tipo_equipamento=HistoricoMovimentacaoEquipamento.TipoEquipamento.EPI,
                    epi=item,
                    tipo=HistoricoMovimentacaoEquipamento.TipoOperacao.BAIXA,
                    quantidade=quantidade,
                    usuario=request.user,
                    justificativa=form.cleaned_data.get('justificativa', ''),
                )
            except ValidationError as exc:
                messages.error(
                    request,
                    exc.messages[0] if hasattr(exc, 'messages') else str(exc),
                )
            else:
                messages.success(
                    request,
                    f'Baixa de {quantidade} unidade(s) registrada. '
                    f'Estoque atual: {item.estoque_disponivel}.',
                )
                return redirect('equipamentos:detalhe_epi', pk=item.pk)
    else:
        form = BaixaEPIForm()
    return render(
        request,
        'equipamentos/baixa_epi.html',
        {'form': form, 'item': item},
    )


@login_required
def lista_epcs(request):
    itens = EPC.objects.all()
    return render(request, 'equipamentos/lista_epcs.html', {'itens': itens})


@login_required
def detalhe_epc(request, pk):
    item = get_object_or_404(EPC, pk=pk)
    historico = item.movimentacoes.select_related('usuario')[:10]
    return render(
        request,
        'equipamentos/detalhe_epc.html',
        {'item': item, 'historico': historico},
    )


@login_required
@requer_staff
def cadastrar_epc(request):
    if request.method == 'POST':
        form = EPCForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'EPC cadastrado com sucesso!')
            return redirect('equipamentos:lista_epcs')
    else:
        form = EPCForm()
    return render(
        request,
        'equipamentos/form_epc.html',
        {'form': form, 'titulo': 'Cadastrar EPC'},
    )


@login_required
@requer_staff
def editar_epc(request, pk):
    item = get_object_or_404(EPC, pk=pk)
    if request.method == 'POST':
        form = EPCForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'EPC atualizado com sucesso!')
            return redirect('equipamentos:detalhe_epc', pk=item.pk)
    else:
        form = EPCForm(instance=item)
    return render(
        request,
        'equipamentos/form_epc.html',
        {'form': form, 'titulo': f'Editar EPC — {item.nome}', 'item': item},
    )


@login_required
@requer_staff
def registrar_inspecao_epc(request, pk):
    item = get_object_or_404(EPC, pk=pk)
    if request.method == 'POST':
        form = InspecaoEPCForm(request.POST)
        if form.is_valid():
            obs = form.cleaned_data.get('observacoes', '')
            item.registrar_inspecao(
                data_inspecao=form.cleaned_data['data_inspecao'],
                observacoes=obs,
            )
            HistoricoMovimentacaoEquipamento.objects.create(
                tipo_equipamento=HistoricoMovimentacaoEquipamento.TipoEquipamento.EPC,
                epc=item,
                tipo=HistoricoMovimentacaoEquipamento.TipoOperacao.INSPECAO,
                usuario=request.user,
                justificativa=obs,
            )
            messages.success(
                request,
                f'Inspeção registrada. Próxima inspeção: '
                f'{item.data_proxima_inspecao:%d/%m/%Y}.',
            )
            return redirect('equipamentos:detalhe_epc', pk=item.pk)
    else:
        form = InspecaoEPCForm()
    return render(
        request,
        'equipamentos/inspecao_epc.html',
        {'form': form, 'item': item},
    )


@login_required
@requer_staff
def movimentacao_equipamento(request):
    """Tela unificada de movimentação de EPI/EPC (somente staff)."""
    if request.method == 'POST':
        form = MovimentacaoEquipamentoForm(request.POST)
        if form.is_valid():
            tipo_eq = form.cleaned_data['tipo_equipamento']
            tipo = form.cleaned_data['tipo']
            justificativa = form.cleaned_data.get('justificativa', '')

            try:
                if tipo_eq == 'EPI':
                    epi = form.cleaned_data['epi']
                    quantidade = form.cleaned_data['quantidade']
                    epi.aplicar_ajuste_estoque(quantidade, tipo)
                    HistoricoMovimentacaoEquipamento.objects.create(
                        tipo_equipamento=HistoricoMovimentacaoEquipamento.TipoEquipamento.EPI,
                        epi=epi,
                        tipo=tipo,
                        quantidade=quantidade,
                        usuario=request.user,
                        justificativa=justificativa,
                    )
                    messages.success(
                        request,
                        f'Movimentação de {tipo} registrada para {epi.nome}. '
                        f'Estoque atual: {epi.estoque_disponivel}.',
                    )
                else:
                    epc = form.cleaned_data['epc']
                    epc.registrar_inspecao(observacoes=justificativa)
                    HistoricoMovimentacaoEquipamento.objects.create(
                        tipo_equipamento=HistoricoMovimentacaoEquipamento.TipoEquipamento.EPC,
                        epc=epc,
                        tipo=HistoricoMovimentacaoEquipamento.TipoOperacao.INSPECAO,
                        usuario=request.user,
                        justificativa=justificativa,
                    )
                    messages.success(
                        request,
                        f'Inspeção registrada para {epc.nome}. '
                        f'Próxima: {epc.data_proxima_inspecao:%d/%m/%Y}.',
                    )
            except ValidationError as exc:
                messages.error(
                    request,
                    exc.messages[0] if hasattr(exc, 'messages') else str(exc),
                )
            else:
                return redirect('equipamentos:movimentacao')
    else:
        form = MovimentacaoEquipamentoForm()

    ultimas = HistoricoMovimentacaoEquipamento.objects.select_related(
        'epi', 'epc', 'usuario'
    )[:10]
    return render(
        request,
        'equipamentos/movimentacao.html',
        {'form': form, 'ultimas': ultimas},
    )
