from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import formset_factory
from .models import Cliente, Pedido, OrdemDeServico, Produto, Pagamento  # Importe o modelo Pagamento
from .forms import (
    ClienteForm, PedidoForm, OrdemDeServicoForm, OrdemDeServicoFormSet,
    ProdutoForm, CustoForm, PagamentoForm
)
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from .utils import gerar_contrato_pdf, enviar_contrato_email
from django.db import transaction


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
    produtos = Produto.objects.all()  # Obtém todos os produtos

    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        ordem_de_servico_formset = OrdemDeServicoFormSet(request.POST, request.FILES,
                                                         prefix='ordem_de_servico')

        if pedido_form.is_valid() and ordem_de_servico_formset.is_valid():
            pedido = pedido_form.save()  # Salva o pedido imediatamente
            valor_total = 0

            for form in ordem_de_servico_formset:
                if form.has_changed():
                    ordem_de_servico = form.save(commit=False)  # Não salva ainda

                    # Calcula a soma dos tamanhos
                    soma_tamanhos = (
                            (ordem_de_servico.pp_masculino or 0) + (ordem_de_servico.pp_feminino or 0) +
                            (ordem_de_servico.p_masculino or 0) + (ordem_de_servico.p_feminino or 0) +
                            (ordem_de_servico.m_masculino or 0) + (ordem_de_servico.m_feminino or 0) +
                            (ordem_de_servico.g_masculino or 0) + (ordem_de_servico.g_feminino or 0) +
                            (ordem_de_servico.gg_masculino or 0) + (ordem_de_servico.gg_feminino or 0) +
                            (ordem_de_servico.xg_masculino or 0) + (ordem_de_servico.xg_feminino or 0) +
                            (ordem_de_servico.esp_masculino or 0) + (ordem_de_servico.esp_feminino or 0)
                    )

                    # Verifica se a quantidade informada corresponde à soma da grade de tamanhos
                    if ordem_de_servico.quantidade_digitada != soma_tamanhos:
                        context = {
                            'pedido_form': pedido_form,
                            'ordem_de_servico_formset': ordem_de_servico_formset,
                            'produtos': produtos,
                            'mensagem_erro': 'Quantidade diferente da soma da grade de tamanhos.'
                        }
                        return render(request, 'kq_app/novo_pedido.html', context)

                    # Se a validação passou, salva a ordem de serviço
                    ordem_de_servico.pedido = pedido
                    ordem_de_servico.save()

                    valor_total += ordem_de_servico.preco_unitario * ordem_de_servico.quantidade

            # Se todas as validações passaram, salva o pedido
            pedido.valor_total = valor_total + pedido_form.cleaned_data['frete']
            pedido.save()

            return redirect('detalhes_pedido', pedido_id=pedido.id)
        else:
            messages.error(request, 'Erro ao cadastrar pedido. Verifique os dados.')
    else:
        pedido_form = PedidoForm()
        ordem_de_servico_formset = OrdemDeServicoFormSet(prefix='ordem_de_servico')

    context = {
        'pedido_form': pedido_form,
        'ordem_de_servico_formset': ordem_de_servico_formset,
        'produtos': produtos,  # Passa a lista de produtos para o template
        'mensagem_erro': None  # Inicializa a mensagem de erro como None
    }
    return render(request, 'kq_app/novo_pedido.html', context)


def detalhes_pedido(request, pedido_id):
    """Mostra os detalhes de um pedido, incluindo ordens de serviço, pagamentos,
    total pago e saldo restante. Utiliza a agregação do Django para calcular o total pago.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    ordens_de_servico = OrdemDeServico.objects.filter(pedido=pedido)

    # Utiliza a função de agregação Sum do Django para calcular o total pago
    pagamentos = Pagamento.objects.filter(pedido=pedido)
    total_pago = pagamentos.aggregate(total=Sum('valor_pago'))['total'] or 0

    # Calcula o saldo restante
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
            return redirect('gerenciar_produtos')
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


def atualizar_status_pedido(request, pedido_id):
    """Atualiza o status de um pedido via POST."""
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in dict(Pedido.STATUS_CHOICES):
            pedido.status = novo_status
            pedido.save()
            return JsonResponse({'status': 'success', 'message': 'Status atualizado com sucesso!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Status inválido.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido.'}, status=405)


def gerar_folha_corte_costura(request, os_id):
    ordem_de_servico = get_object_or_404(OrdemDeServico, pk=os_id)
    pedido = ordem_de_servico.pedido

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="folha_corte_costura_OS_{os_id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle(f"Folha de Corte e Costura - OS {os_id}")

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.alignment = 1  # ALIGN_CENTER

    # Cores do HTML (substitua pelos valores exatos)
    cor_principal = colors.HexColor("#3D3D6A")  # Cor do cabeçalho
    cor_fundo_tabela = colors.HexColor("#f0f0f0")  # Cor do fundo das células de cabeçalho da tabela

    x_start = inch
    y_start = letter[1] - 0.25 * inch  # Diminui ainda mais a margem superior
    line_height = 0.5 * inch

    # Tabela com informações do pedido e OS (canto superior direito)
    data_tabela_info = [
        ["Pedido:", pedido.id],
        ["OS:", ordem_de_servico.numero_os]
    ]
    tabela_info = Table(data_tabela_info, colWidths=[2.5 * inch, 2.5 * inch])
    tabela_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 1), cor_fundo_tabela),
        ('TEXTCOLOR', (0, 0), (1, 1), colors.black),
        ('ALIGN', (0, 0), (1, 1), 'LEFT'),  # Alinha à esquerda
        ('FONTNAME', (0, 0), (1, 1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 1), 6),
        ('GRID', (0, 0), (1, 1), 1, colors.black)
    ]))
    tabela_info.wrapOn(p, 5 * inch, 2 * inch)
    tabela_info.drawOn(p, letter[0] - 6 * inch, y_start - 2 * line_height)

    # Mockup centralizado acima
    img_width = 4 * inch
    img_height = 3 * inch
    img_x = (letter[0] - img_width) / 2
    img_y = y_start - 3 * line_height - img_height  # Reduz o espaço acima da imagem

    if ordem_de_servico.mockup:
        mockup_path = ordem_de_servico.mockup.path
        try:
            img = Image(mockup_path, width=img_width, height=img_height)
            img.drawOn(p, img_x, img_y)
        except Exception as e:
            p.setFont("Helvetica", 10)
            p.drawString(img_x, img_y, f"Erro ao carregar o mockup: {e}")

    # Tabela com informações da OS
    data_tabela_os = [
        ["Produto", ordem_de_servico.produto.nome],  # Mescla as células
        ["Cor do Tecido", ordem_de_servico.cor_tecido or "Não especificada"],
        ["Data de Início", pedido.data_criacao.strftime('%d/%m/%Y')],
        ["Prazo", pedido.data_entrega.strftime('%d/%m/%Y') if pedido.data_entrega else "Não Definido"],
    ]
    tabela_os = Table(data_tabela_os, colWidths=[2.5 * inch, 3 * inch])
    tabela_os.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), cor_fundo_tabela),  # Aplica a cor de fundo apenas à primeira coluna
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centraliza o texto
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (0, -1), 6),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Centraliza o texto na segunda coluna
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    tabela_os_y = img_y - 4 * line_height  # Posiciona a tabela abaixo da imagem
    tabela_os.wrapOn(p, 5.5 * inch, 5 * inch)
    tabela_os.drawOn(p, (letter[0] - 5.5 * inch) / 2, tabela_os_y)  # Centraliza a tabela

    # Tabela de tamanhos centralizada
    data_tabela_tamanhos = [
        ["Tamanho", "Masculino", "Feminino"],
        ["PP", ordem_de_servico.pp_masculino, ordem_de_servico.pp_feminino],
        ["P", ordem_de_servico.p_masculino, ordem_de_servico.p_feminino],
        ["M", ordem_de_servico.m_masculino, ordem_de_servico.m_feminino],
        ["G", ordem_de_servico.g_masculino, ordem_de_servico.g_feminino],
        ["GG", ordem_de_servico.gg_masculino, ordem_de_servico.gg_feminino],
        ["XG", ordem_de_servico.xg_masculino, ordem_de_servico.xg_feminino],
        ["ESP", ordem_de_servico.esp_masculino, ordem_de_servico.esp_feminino]
    ]
    tabela_tamanhos = Table(data_tabela_tamanhos, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch])
    tabela_tamanhos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), cor_fundo_tabela),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
        ('ALIGN', (0, 0), (2, 7), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('GRID', (0, 0), (2, 7), 1, colors.black)
    ]))
    tabela_tamanhos_y = 2 * inch  # Espaçamento mínimo
    tabela_tamanhos.wrapOn(p, 4.5 * inch, 5 * inch)
    tabela_tamanhos.drawOn(p, (letter[0] - 4.5 * inch) / 2, tabela_os_y - 5 * line_height)  # Posiciona abaixo da tabela de informações

    # Observações da OS
    p.setFont("Helvetica-Bold", 12)
    obs_y = tabela_os_y - 6 * line_height  # Define a posição Y das observações abaixo da tabela de tamanhos
    p.drawString((letter[0] - 5.5 * inch) / 2, obs_y, f"Observações da OS: {ordem_de_servico.observacoes or 'Nenhuma observação.'}")  # Centraliza as observações

    p.showPage()
    p.save()
    return response

# def aprovar_pedido(request, pedido_id):
  #  pedido = get_object_or_404(Pedido, id=pedido_id)
   # pedido.status = 'aprovado'
    #pedido.save()

    # Gerar o contrato em PDF
    #pdf_file = gerar_contrato_pdf(pedido)

    # Enviar o contrato por e-mail
#    enviar_contrato_email(pedido, pdf_file)

#    messages.success(request, 'Pedido aprovado e contrato enviado por e-mail!')
 #   return redirect('detalhes_pedido', pedido_id=pedido.id)

def gerar_contrato_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pdf_file = gerar_contrato_pdf(pedido)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrato_pedido_{pedido.id}.pdf"'
    return response

def excluir_pedido(request, pedido_id):
    """
    Exclui um pedido e todas as suas dependências (ordens de serviço e pagamentos)
    de forma transacional. Isso garante que, se a exclusão de qualquer dependência falhar,
    todo o processo seja revertido, mantendo a integridade dos dados.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)

    try:
        with transaction.atomic():
            # Exclui todas as ordens de serviço associadas ao pedido
            OrdemDeServico.objects.filter(pedido=pedido).delete()

            # Exclui todos os pagamentos associados ao pedido
            Pagamento.objects.filter(pedido=pedido).delete()

            # Finalmente, exclui o pedido
            pedido.delete()

        messages.success(request, 'Pedido e todos os seus detalhes (ordens de serviço e pagamentos) excluídos com sucesso!')

    except Exception as e:
        messages.error(request, f'Erro ao excluir pedido: {e}. Consulte os logs para mais detalhes.')
        # Aqui, você pode adicionar logging para registrar o erro detalhadamente
        # import logging
        # logging.error(f"Erro ao excluir pedido {pedido_id}: {e}", exc_info=True)

    return redirect('visualizar_producao')
