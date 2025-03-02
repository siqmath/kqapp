from django.urls import path
from . import views
from .views import gerenciar_produtos, excluir_produto   # Certifique-se de que suas views estão importadas corretamente

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('novo_pedido/', views.novo_pedido, name='novo_pedido'),  # Página para criar um novo pedido
    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),  # Página para cadastrar cliente
    path('editar_pedido/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),  # Página para editar um pedido
    path('acompanhar_pedidos', views.visualizar_producao, name='visualizar_producao'),  # Página para visualizar produção
    path('gerenciar_estoque/', views.adicionar_custo, name='gerenciar_estoque'),  # Página para adicionar custo
    path('detalhes_pedido/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),  # URL para detalhes do pedido
    path('controle_financeiro/', views.controle_financeiro, name='controle_financeiro'),  # Página para controle financeiro
    path('lista_compra/', views.lista_compra, name='lista_compra'),  # Página para lista de compra
    path('corteecostura/', views.corteecostura, name='corteecostura'),  # Página para corte e costura
    path('visualizar_producao', views.visualizar_producao, name='visualizar_producao'),
    path('gerenciar_produtos', views.gerenciar_produtos, name='gerenciar_produtos'),
    path('excluir_produto/<int:produto_id>/', excluir_produto, name='excluir_produto'),
]