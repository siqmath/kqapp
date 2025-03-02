# kq_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Cliente, Pedido, OrdemDeServico, Produto, TipoProduto, Material, QuantidadeTamanho
from .forms import PedidoForm, OrdemDeServicoForm, ClienteForm, QuantidadeTamanhoFormSet

def home(request):
    return render(request, 'kq_app/home.html')

def novo_pedido(request):
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        quantidade_formset = QuantidadeTamanhoFormSet(request.POST)
        
        if pedido_form.is_valid() and quantidade_formset.is_valid():
            # Salva o pedido primeiro
            pedido = pedido_form.save()
            
            # Cria a ordem de serviço associada
            ordem = OrdemDeServico.objects.create(pedido=pedido)
            
            # Salva as quantidades/tamanhos
            quantidades = quantidade_formset.save(commit=False)
            for qtd in quantidades:
                qtd.ordem_servico = ordem
                qtd.save()
            
            messages.success(request, f"Pedido {pedido.numero} criado com sucesso!")
            return redirect('visualizar_producao')

    else:
        pedido_form = PedidoForm()
        quantidade_formset = QuantidadeTamanhoFormSet()

    context = {
        'pedido_form': pedido_form,
        'quantidade_formset': quantidade_formset,
        'clientes': Cliente.objects.all(),
        'produtos': Produto.objects.all()
    }
    return render(request, 'kq_app/novo_pedido.html', context)

def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'kq_app/cadastrar_cliente.html', {'form': form})

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.prefetch_related('ordens_servico'), id=pedido_id)
    
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST, instance=pedido)
        
        if pedido_form.is_valid():
            pedido_form.save()
            messages.success(request, "Pedido atualizado com sucesso!")
            return redirect('detalhes_pedido', pedido_id=pedido.id)

    else:
        pedido_form = PedidoForm(instance=pedido)

    return render(request, 'kq_app/editar_pedido.html', {
        'form': pedido_form,
        'pedido_id': pedido_id
    })

def visualizar_producao(request):
    pedidos = Pedido.objects.all().prefetch_related('ordens_servico')
    return render(request, 'kq_app/visualizar_producao.html', {'pedidos': pedidos})

def adicionar_custo(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'kq_app/adicionar_custo.html')

def controle_financeiro(request):
    return render(request, 'kq_app/controle_financeiro.html')

def lista_compra(request):
    return render(request, 'kq_app/lista_compra.html')

def corteecostura(request):
    ordens = OrdemDeServico.objects.filter(estado_atual__in=['corte', 'costura'])
    return render(request,'kq_app/corteecostura.html',{'ordens':ordens})

def gerenciar_produtos(request):
    if request.method =='POST':
        tipo_nome=request.POST.get('tipo')
        material_nome=request.POST.get('material')
        
        tipo_obj,_=TipoProduto.objects.get_or_create(nome=tipo_nome)
        material_obj,_=Material.objects.get_or_create(nome=material_nome)
        
        Produto.objects.create(
           tipo=tipo_obj,
           material=material_obj,
           rendimento=request.POST.get('rendimento') 
         )
    return redirect('gerenciar_produtos')

    produtos=Produto.objects.select_related('tipo','material').all()
    return render(
         request,
         'kq_app/gerenciar_produtos.html',
         {'produtos':produtos}
     )

def excluir_produto(request,pk):
     produto=get_object_or_404(Produto,pk=pk)
     produto.delete()
     messages.success(
         request,
         f"Produto {produto.tipo} - {produto.material} excluído!"
     )
     return redirect('gerenciar_produtos')

def detalhes_pedido(requset,pk): 
     pediao=get_object_or_404(
         Pediao.objects.prefetch_realted(
             'ordens_servicco__quantidadetaminho_set'
         ),
         pk=pk 
     )
     
     tamanhos={'Masculino':{},'Feminino':{}}
     
     for os in pediao.ordens_servicco.all():
         for qt in os.quantidadetaminho_set.all():
             genero=qt.genero 
             tamanho=qt.taminho 
             total=tamanhos[genero].get(taminho ,0)+qt.quantidadde 
             tamanhos[genero][taminh]=total 
    
     context={
         'pediao':pediao ,
         'tamanhos_masc':tamanhos['Masculino'],
         'tamnhos_femi':tamnhaos['Feminino']
     } 
    
     return renser(
         requset,
         'kq_app/detalhes_pediao.html',
          context 
      ) 

# Mantidas as demais funções conforme necessidade do projeto