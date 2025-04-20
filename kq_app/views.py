from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import formset_factory
from .models import Cliente, Pedido, OrdemDeServico, Produto, Pagamento, ContatoCliente, EtapaRelacionamento, NotaInterna, Estoque
from .forms import (
    ClienteForm, PedidoForm, OrdemDeServicoForm, OrdemDeServicoFormSet,
    ProdutoForm, CustoForm, PagamentoForm, ContatoClienteForm, EtapaRelacionamentoForm, NotaInternaForm, EntradaEstoqueForm
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
from django.utils.html import format_html
from django.db import transaction
from django.core.paginator import Paginator
import logging

def home(request):
    """Página inicial."""
    return render(request, 'kq_app/home.html')
    
def cadastrar_cliente(request):
    busca = request.GET.get('busca', '')
    clientes = Cliente.objects.filter(nome__icontains=busca).order_by('nome')
    paginator = Paginator(clientes, 5)
    pagina = request.GET.get('pagina')
    clientes = paginator.get_page(pagina)

    form = ClienteForm()
    editando = None

    if request.method == 'POST':
        # Edição de cliente existente
        if 'editar_cliente_id' in request.POST:
            cliente = get_object_or_404(Cliente, id=request.POST['editar_cliente_id'])
            form = ClienteForm(request.POST, instance=cliente)
            editando = cliente.id

        # Exclusão de cliente e dados relacionados
        elif 'excluir_cliente_id' in request.POST:
            cliente = get_object_or_404(Cliente, id=request.POST['excluir_cliente_id'])
            try:
                with transaction.atomic():
                    NotaInterna.objects.filter(cliente=cliente).delete()
                    ContatoCliente.objects.filter(cliente=cliente).delete()
                    EtapaRelacionamento.objects.filter(cliente=cliente).delete()

                    pedidos = Pedido.objects.filter(cliente=cliente)
                    for pedido in pedidos:
                        OrdemDeServico.objects.filter(pedido=pedido).delete()
                        Pagamento.objects.filter(pedido=pedido).delete()
                        pedido.delete()

                    cliente.delete()

                messages.success(request, 'Cliente e todos os dados relacionados excluídos com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao excluir cliente: {e}')
            return redirect('cadastrar_cliente')

        # Cadastro de novo cliente
        else:
            form = ClienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente salvo com sucesso.')
            return redirect('cadastrar_cliente')

    elif 'editar' in request.GET:
        cliente = get_object_or_404(Cliente, id=request.GET['editar'])
        form = ClienteForm(instance=cliente)
        editando = cliente.id

    context = {
        'form': form,
        'clientes': clientes,
        'busca': busca,
        'editando': editando,
    }
    return render(request, 'kq_app/cadastrar_cliente.html', context)

def cliente_detalhes(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        contatos = ContatoCliente.objects.filter(cliente=cliente).order_by('-data_contato')
        notas = NotaInterna.objects.filter(cliente=cliente).order_by('-data')

        etapa_qs = EtapaRelacionamento.objects.filter(cliente=cliente)
        if etapa_qs.count() > 1:
            etapa_qs.exclude(id=etapa_qs.first().id).delete()
        etapa, _ = EtapaRelacionamento.objects.get_or_create(cliente=cliente)

        contato_form = ContatoClienteForm()
        nota_form = NotaInternaForm()
        etapa_form = EtapaRelacionamentoForm(instance=etapa)

        if request.method == 'POST':
            if 'add_contato' in request.POST:
                contato_form = ContatoClienteForm(request.POST)
                if contato_form.is_valid():
                    contato = contato_form.save(commit=False)
                    contato.cliente = cliente
                    contato.save()
                    messages.success(request, 'Contato registrado com sucesso.')
                    return redirect('cliente_detalhes', cliente_id=cliente.id)

            elif 'add_nota' in request.POST:
                nota_form = NotaInternaForm(request.POST)
                if nota_form.is_valid():
                    nota = nota_form.save(commit=False)
                    nota.cliente = cliente
                    nota.save()
                    messages.success(request, 'Nota adicionada com sucesso.')
                    return redirect('cliente_detalhes', cliente_id=cliente.id)

            elif 'update_etapa' in request.POST:
                etapa_form = EtapaRelacionamentoForm(request.POST, instance=etapa)
                if etapa_form.is_valid():
                    etapa_form.save()
                    messages.success(request, 'Etapa de relacionamento atualizada.')
                    return redirect('cliente_detalhes', cliente_id=cliente.id)

        context = {
            'cliente': cliente,
            'contatos': contatos,
            'notas': notas,
            'etapa': etapa,
            'contato_form': contato_form,
            'nota_form': nota_form,
            'etapa_form': etapa_form,
        }
        return render(request, 'kq_app/cliente_detalhes.html', context)

    except Exception as e:
        logging.error(f"Erro na view cliente_detalhes para cliente_id={cliente_id}: {e}", exc_info=True)
        return HttpResponse(f"Erro interno ao carregar cliente {cliente_id}: {e}", status=500)

def novo_pedido(request):
    produtos = Produto.objects.all()
    busca = request.GET.get('busca', '')

    # Filtra os clientes, se houver busca por nome
    if busca:
        clientes_filtrados = Cliente.objects.filter(nome__icontains=busca)
        pedido_form = PedidoForm()
        pedido_form.fields['cliente'].queryset = clientes_filtrados
    else:
        pedido_form = PedidoForm()

    OrdemDeServicoFormSetFactory = formset_factory(OrdemDeServicoForm, extra=1, can_delete=True)

    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        ordem_de_servico_formset = OrdemDeServicoFormSetFactory(request.POST, request.FILES, prefix='ordem_de_servico')

        if pedido_form.is_valid() and ordem_de_servico_formset.is_valid():
            pedido = pedido_form.save()
            valor_total = 0

            for form in ordem_de_servico_formset:
                if form.has_changed():
                    os = form.save(commit=False)

                    soma_tamanhos = (
                        (os.pp_masculino or 0) + (os.pp_feminino or 0) +
                        (os.p_masculino or 0) + (os.p_feminino or 0) +
                        (os.m_masculino or 0) + (os.m_feminino or 0) +
                        (os.g_masculino or 0) + (os.g_feminino or 0) +
                        (os.gg_masculino or 0) + (os.gg_feminino or 0) +
                        (os.xg_masculino or 0) + (os.xg_feminino or 0) +
                        (os.esp_masculino or 0) + (os.esp_feminino or 0)
                    )

                    if os.quantidade_digitada != soma_tamanhos:
                        context = {
                            'pedido_form': pedido_form,
                            'ordem_de_servico_formset': ordem_de_servico_formset,
                            'produtos': produtos,
                            'mensagem_erro': 'Quantidade diferente da soma da grade de tamanhos.'
                        }
                        return render(request, 'kq_app/novo_pedido.html', context)

                    os.pedido = pedido
                    os.save()
                    valor_total += os.preco_unitario * os.quantidade

            pedido.valor_total = valor_total + pedido_form.cleaned_data.get('frete', 0)
            pedido.save()

            return redirect('detalhes_pedido', pedido_id=pedido.id)

        else:
            ordem_de_servico_formset = OrdemDeServicoFormSetFactory(request.POST, request.FILES, prefix='ordem_de_servico')
            messages.error(request, 'Erro ao cadastrar pedido. Verifique os dados.')

    else:
        ordem_de_servico_formset = OrdemDeServicoFormSetFactory(prefix='ordem_de_servico')

    context = {
        'pedido_form': pedido_form,
        'ordem_de_servico_formset': ordem_de_servico_formset,
        'produtos': produtos,
        'mensagem_erro': None
    }
    return render(request, 'kq_app/novo_pedido.html', context)

def detalhes_pedido(request, pedido_id):
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        ordens_de_servico = pedido.ordens_de_servico.all()
        pagamentos = Pagamento.objects.filter(pedido=pedido)
        total_pago = pagamentos.aggregate(total=models.Sum('valor_pago'))['total'] or 0
        saldo_restante = pedido.valor_total - total_pago

        context = {
            'pedido': pedido,
            'ordens_de_servico': ordens_de_servico,
            'pagamentos': pagamentos,
            'total_pago': total_pago,
            'saldo_restante': saldo_restante,
        }
        return render(request, 'kq_app/detalhes_pedido.html', context)

    except Exception as e:
        logging.error(f"Erro ao carregar detalhes do pedido {pedido_id}: {e}", exc_info=True)
        return HttpResponse(f"Erro interno ao carregar pedido {pedido_id}: {e}", status=500)

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
    pedido = get_object_or_404(Pedido, id=pedido_id)

    try:
        with transaction.atomic():
            OrdemDeServico.objects.filter(pedido=pedido).delete()
            Pagamento.objects.filter(pedido=pedido).delete()
            pedido.delete()
            messages.success(request, 'Pedido e seus dados relacionados foram excluídos com sucesso.')
    except Exception as e:
        logging.error(f"Erro ao excluir pedido {pedido_id}: {e}", exc_info=True)
        messages.error(request, f'Erro ao excluir pedido: {str(e)}')

    return redirect('visualizar_producao')


def adicionar_contato_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ContatoClienteForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.cliente = cliente
            contato.save()
            messages.success(request, 'Contato registrado com sucesso.')
    return redirect('cliente_detalhes', cliente_id=cliente.id)

def adicionar_nota_interna(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = NotaInternaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.cliente = cliente
            nota.save()
            messages.success(request, 'Nota interna salva com sucesso.')
    return redirect('cliente_detalhes', cliente_id=cliente.id)

def atualizar_etapa_relacionamento(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    etapa, _ = EtapaRelacionamento.objects.get_or_create(cliente=cliente)
    if request.method == 'POST':
        form = EtapaRelacionamentoForm(request.POST, instance=etapa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etapa de relacionamento atualizada.')
    return redirect('cliente_detalhes', cliente_id=cliente.id)

def exportar_csv(request):
    tipo = request.GET.get('tipo')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{tipo}_financeiro_kq.csv"'

    writer = csv.writer(response)

    if tipo == 'faturamento':
        writer.writerow(['Pedido', 'Cliente', 'Produto', 'Data Entrega', 'Quantidade', 'Valor Unitário', 'Valor Total'])
        for pedido in Pedido.objects.prefetch_related('ordens_de_servico').select_related('cliente'):
            for os in pedido.ordens_de_servico.all():
                writer.writerow([
                    pedido.id,
                    pedido.cliente.nome,
                    os.produto.nome,
                    pedido.data_entrega.strftime('%d/%m/%Y') if pedido.data_entrega else 'Não definida',
                    os.quantidade,
                    f"{os.preco_unitario:.2f}",
                    f"{os.preco_unitario * os.quantidade:.2f}"
                ])

    elif tipo == 'custos':
        writer.writerow(['Pedido', 'Cliente', 'Produto', 'Tipo de Custo', 'Valor', 'Data'])
        for custo in Custo.objects.select_related('ordem_de_servico__pedido', 'ordem_de_servico__produto'):
            writer.writerow([
                custo.ordem_de_servico.pedido.id,
                custo.ordem_de_servico.pedido.cliente.nome,
                custo.ordem_de_servico.produto.nome,
                custo.tipo or 'Outro',
                f"{custo.valor:.2f}",
                custo.data.strftime('%d/%m/%Y')
            ])

    elif tipo == 'resultado':
        writer.writerow(['Pedido', 'Cliente', 'Produto', 'Entrega', 'Valor Total', 'Custos', 'Lucro'])
        for pedido in Pedido.objects.prefetch_related('ordens_de_servico').select_related('cliente'):
            subtotal = 0
            custo_total = 0
            produtos = []
            for os in pedido.ordens_de_servico.all():
                produtos.append(os.produto.nome)
                subtotal += os.preco_unitario * os.quantidade
                custo_total += sum(c.valor for c in Custo.objects.filter(ordem_de_servico=os))
            writer.writerow([
                pedido.id,
                pedido.cliente.nome,
                ", ".join(produtos),
                pedido.data_entrega.strftime('%d/%m/%Y') if pedido.data_entrega else 'Não definida',
                f"{subtotal:.2f}",
                f"{custo_total:.2f}",
                f"{(subtotal - custo_total):.2f}"
            ])

    return response


def resumo_financeiro(request):
    pedidos = Pedido.objects.prefetch_related('ordens_de_servico').select_related('cliente')

    filtro_cliente = request.GET.get('cliente')
    filtro_data_inicio = request.GET.get('data_inicio')
    filtro_data_fim = request.GET.get('data_fim')
    filtro_produto = request.GET.get('produto')

    if filtro_cliente:
        pedidos = pedidos.filter(cliente__nome__icontains=filtro_cliente)

    if filtro_data_inicio:
        pedidos = pedidos.filter(data_criacao__gte=filtro_data_inicio)

    if filtro_data_fim:
        pedidos = pedidos.filter(data_criacao__lte=filtro_data_fim)

    linhas_faturamento = []
    linhas_resultado = []
    linhas_custos = []

    for pedido in pedidos:
        ordens = pedido.ordens_de_servico.all()
        subtotal = 0
        custo_total = 0

        for os in ordens:
            if filtro_produto and filtro_produto.lower() not in os.produto.nome.lower():
                continue

            quantidade = os.quantidade
            total = os.preco_unitario * quantidade
            subtotal += total

            custos_os = Custo.objects.filter(ordem_de_servico=os)
            for custo in custos_os:
                custo_total += custo.valor

            linhas_faturamento.append(f"""
                <tr>
                    <td>{pedido.id}</td>
                    <td>{pedido.cliente.nome}</td>
                    <td>{os.produto.nome}</td>
                    <td>{pedido.data_entrega.strftime('%d/%m/%Y') if pedido.data_entrega else 'Não definida'}</td>
                    <td>{quantidade}</td>
                    <td>R$ {os.preco_unitario:.2f}</td>
                    <td>R$ {total:.2f}</td>
                </tr>
            """)

        custos_pedido = Custo.objects.filter(ordem_de_servico__pedido=pedido)
        for custo in custos_pedido:
            linhas_custos.append(f"""
                <tr>
                    <td>{pedido.id}</td>
                    <td>{pedido.cliente.nome}</td>
                    <td>{custo.ordem_de_servico.produto.nome}</td>
                    <td>{custo.tipo or 'Outro'}</td>
                    <td>R$ {custo.valor:.2f}</td>
                    <td>{custo.data.strftime('%d/%m/%Y')}</td>
                </tr>
            """)

        linhas_resultado.append(f"""
            <tr>
                <td>{pedido.id}</td>
                <td>{pedido.cliente.nome}</td>
                <td>{', '.join([os.produto.nome for os in ordens])}</td>
                <td>{pedido.data_entrega.strftime('%d/%m/%Y') if pedido.data_entrega else 'Não definida'}</td>
                <td>R$ {subtotal:.2f}</td>
                <td>R$ {custo_total:.2f}</td>
                <td>R$ {(subtotal - custo_total):.2f}</td>
            </tr>
        """)

    tabela_faturamento = format_html("""
        <tbody>{}</tbody>
    """, format_html("".join(linhas_faturamento)))

    tabela_custos = format_html("""
        <tbody>{}</tbody>
    """, format_html("".join(linhas_custos)))

    tabela_resultado = format_html("""
        <tbody>{}</tbody>
    """, format_html("".join(linhas_resultado)))

    return render(request, 'kq_app/resumo_financeiro.html', {
        'tabela_faturamento': tabela_faturamento,
        'tabela_custos': tabela_custos,
        'tabela_resultado': tabela_resultado,
        'produtos': Produto.objects.all()
    })


