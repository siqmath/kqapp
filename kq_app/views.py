# kq_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import Cliente, Pedido, OrdemDeServico, Produto, Estoque, Custo, Pagamento
from .forms import (
    ClienteForm, PedidoForm, OrdemDeServicoForm, OrdemDeServicoFormSet, 
    ProdutoForm, CustoForm, PagamentoForm
)

def home(request):
    """Página inicial."""
    return render(request, 'kq_app/home.html')

def cadastrar_cliente(request):
    """Cadastra um novo cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('home')  # Redireciona para a página inicial
        else:
            messages.error(request, 'Erro ao cadastrar cliente. Verifique os dados.')
    else:
        form = ClienteForm()
    return render(request, 'kq_app/cadastrar_cliente.html', {'form': form})

def novo_pedido(request):
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        ordem_de_servico_formset = OrdemDeServicoFormSet(request.POST, request.FILES)

        if pedido_form.is_valid() and ordem_de_servico_formset.is_valid():
            pedido = pedido_form.save(commit=False)
            pedido.cliente = pedido_form.clean_cliente()
            pedido.save()

            for form in ordem_de_servico_formset:
                if form.cleaned_data:
                    ordem_de_servico = form.save(commit=False)
                    ordem_de_servico.pedido = pedido
                    ordem_de_servico.save()

            return redirect('lista_pedidos')  # Redireciona para a listagem de pedidos
    else:
        pedido_form = PedidoForm()
        ordem_de_servico_formset = OrdemDeServicoFormSet()

    produtos = Produto.objects.all()
    return render(request, 'kq_app/novo_pedido.html', {
        'pedido_form': pedido_form,
        'ordem_de_servico_formset': ordem_de_servico_formset,
        'produtos': produtos,
    })

def editar_pedido(request, pedido_id):
    """Edita um pedido existente."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST, instance=pedido)
        if pedido_form.is_valid():
            pedido_form.save()
            messages.success(request, "Pedido atualizado com sucesso!")
            return redirect('detalhes_pedido', pedido_id=pedido.id)
        else:
            messages.error(request, 'Erro ao atualizar pedido. Verifique os dados.')
    else:
        pedido_form = PedidoForm(instance=pedido)
    return render(request, 'kq_app/editar_pedido.html', {'form': pedido_form, 'pedido_id': pedido_id})

def detalhes_pedido(request, pedido_id):
    """Mostra os detalhes de um pedido."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    ordens_de_servico = OrdemDeServico.objects.filter(pedido=pedido)
    pagamentos = Pagamento.objects.filter(pedido=pedido)
    total_pago = sum(pagamento.valor_pago for pagamento in pagamentos)
    saldo_restante = pedido.valor_total - total_pago

    context = {
        'pedido': pedido,
        'ordens_de_servico': ordens_de_servico,
        'pagamentos': pagamentos,
        'total_pago': total_pago,
        'saldo_restante': saldo_restante,
    }
    return render(request, 'kq_app/detalhes_pedido.html', context)

def visualizar_producao(request):
    """Visualiza a produção (lista de pedidos)."""
    pedidos = Pedido.objects.all()
    return render(request, 'kq_app/visualizar_producao.html', {'pedidos': pedidos})

def gerenciar_estoque(request):
    """Gerencia o estoque de produtos."""
    produtos = Produto.objects.all()
    context = {'produtos': produtos}
    return render(request, 'kq_app/gerenciar_estoque.html', context)

def adicionar_custo(request, ordem_de_servico_id):
    """Adiciona um custo a uma ordem de serviço."""
    ordem_de_servico = get_object_or_404(OrdemDeServico, id=ordem_de_servico_id)
    if request.method == 'POST':
        form = CustoForm(request.POST)
        if form.is_valid():
            custo = form.save(commit=False)
            custo.ordem_de_servico = ordem_de_servico
            custo.save()
            messages.success(request, 'Custo adicionado com sucesso!')
            return redirect('detalhes_pedido', pedido_id=ordem_de_servico.pedido.id)
        else:
            messages.error(request, 'Erro ao adicionar custo. Verifique os dados.')
    else:
        form = CustoForm()
    return render(request, 'kq_app/adicionar_custo.html', {'form': form, 'ordem_de_servico': ordem_de_servico})

def controle_financeiro(request):
    """Controla as finanças (lista de pagamentos)."""
    pagamentos = Pagamento.objects.all()
    total_recebido = sum(pagamento.valor_pago for pagamento in pagamentos)
    context = {
        'pagamentos': pagamentos,
        'total_recebido': total_recebido,
    }
    return render(request, 'kq_app/controle_financeiro.html', context)

def adicionar_pagamento(request, pedido_id):
    """Adiciona um pagamento a um pedido."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.pedido = pedido
            pagamento.save()
            messages.success(request, 'Pagamento adicionado com sucesso!')
            return redirect('detalhes_pedido', pedido_id=pedido.id)
        else:
            messages.error(request, 'Erro ao adicionar pagamento. Verifique os dados.')
    else:
        form = PagamentoForm()
    return render(request, 'kq_app/adicionar_pagamento.html', {'form': form, 'pedido': pedido})

def lista_compra(request):
    """Lista de compras (a implementar)."""
    return render(request, 'kq_app/lista_compra.html')

def corteecostura(request):
    """Página de corte e costura (a implementar)."""
    # Ajuste conforme necessário para refletir o estado atual dos pedidos
    pedidos = Pedido.objects.filter(status__in=['em_producao', 'aguardando_aprovacao'])
    return render(request, 'kq_app/corteecostura.html', {'pedidos': pedidos})

def gerenciar_produtos(request):
    """Gerencia os produtos (adicionar, editar, excluir)."""
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('gerenciar_produtos')
        else:
            messages.error(request, 'Erro ao adicionar produto. Verifique os dados.')
    else:
        form = ProdutoForm()

    produtos = Produto.objects.all()
    return render(request, 'kq_app/gerenciar_produtos.html', {'produtos': produtos, 'form': form})

def excluir_produto(request, produto_id):
    """Exclui um produto."""
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        produto.delete()
        messages.success(request, f"Produto {produto.nome} excluído com sucesso!")
        return redirect('gerenciar_produtos')
    return render(request, 'kq_app/excluir_produto.html', {'produto': produto})