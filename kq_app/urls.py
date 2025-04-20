from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('pedidos/novo/', views.novo_pedido, name='novo_pedido'),
    path('pedidos/detalhes/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('producao/acompanhar/', views.visualizar_producao, name='visualizar_producao'),
    path('estoque/gerenciar/', views.gerenciar_estoque, name='gerenciar_estoque'),
    path('custos/adicionar/<int:ordem_de_servico_id>/', views.adicionar_custo, name='adicionar_custo'),
    path('financeiro/controle/', views.controle_financeiro, name='controle_financeiro'),
    path('pagamentos/adicionar/<int:pedido_id>/', views.adicionar_pagamento, name='adicionar_pagamento'),  # Adicione esta linha
    path('lista_compra/', views.lista_compra, name='lista_compra'),
    path('corteecostura/', views.corteecostura, name='corteecostura'),
    path('gerenciar_produtos/', views.gerenciar_produtos, name='gerenciar_produtos'),
    path('excluir_produto/<int:produto_id>/', views.excluir_produto, name='excluir_produto'),
    path('atualizar_status_pedido/<int:pedido_id>/', views.atualizar_status_pedido, name='atualizar_status_pedido'),
    path('folha_corte_costura/<int:os_id>/', views.gerar_folha_corte_costura, name='gerar_folha_corte_costura'),
    path('gerar_contrato/<int:pedido_id>/', views.gerar_contrato_pedido, name='gerar_contrato_pedido'),
    path('excluir_pedido/<int:pedido_id>/', views.excluir_pedido, name='excluir_pedido'),
    path('clientes/<int:cliente_id>/', views.cliente_detalhes, name='cliente_detalhes'),
    path('financeiro/resumo/', views.resumo_financeiro, name='resumo_financeiro'),
    path('resumo_financeiro/', views.exportar_csv, name='exportar_csv'),

]
