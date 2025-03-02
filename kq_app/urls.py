# urls.py
from django.urls import path
from . import views
from .views import gerenciar_produtos, excluir_produto

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('pedidos/novo/', views.novo_pedido, name='novo_pedido'),  # Página para criar um novo pedido
    path('clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),  # Página para cadastrar cliente
    path('pedidos/editar/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),  # Página para editar um pedido
    path('producao/acompanhar/', views.visualizar_producao, name='visualizar_producao'),  # Página para visualizar produção
    path('estoque/gerenciar/', views.gerenciar_estoque, name='gerenciar_estoque'),  # Página para gerenciar estoque
    path('custos/adicionar/', views.adicionar_custo, name='adicionar_custo'),  # Página para adicionar custo
    path('pedidos/detalhes/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),  # URL para detalhes do pedido
    path('financeiro/controle/', views.controle_financeiro, name='controle_financeiro'),  # Página para controle financeiro
    path('compras/lista/', views.lista_compra, name='lista_compra'),  # Página para lista de compra
    path('producao/corteecostura/', views.corteecostura, name='corteecostura'),  # Página para corte e costura
    path('produtos/gerenciar/', views.gerenciar_produtos, name='gerenciar_produtos'),  # Página para gerenciar produtos
    path('produtos/excluir/<int:produto_id>/', excluir_produto, name='excluir_produto'),  # URL para excluir produto
]