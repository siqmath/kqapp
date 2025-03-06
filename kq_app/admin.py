from django.contrib import admin
from .models import Cliente, Produto, Pedido, OrdemDeServico, Custo, Pagamento, Estoque

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cpf_cnpj', 'data_cadastro')
    search_fields = ('nome', 'email', 'cpf_cnpj')
    list_filter = ('data_cadastro',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'material', 'rendimento', 'unidade_medida')
    search_fields = ('nome',)
    list_filter = ('unidade_medida',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data_criacao', 'data_entrega', 'status', 'valor_total')
    list_filter = ('status', 'data_criacao', 'data_entrega')
    search_fields = ('id', 'cliente__nome')
    date_hierarchy = 'data_criacao'

@admin.register(OrdemDeServico)
class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'produto', 'quantidade')
    list_filter = ('produto',)
    search_fields = ('id', 'produto__nome', 'pedido__id')

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade', 'data_atualizacao', 'localizacao')
    search_fields = ('produto__nome', 'localizacao')
    list_filter = ('localizacao',)
    date_hierarchy = 'data_atualizacao'

@admin.register(Custo)
class CustoAdmin(admin.ModelAdmin):
    list_display = ('ordem_de_servico', 'descricao', 'valor', 'data', 'tipo')
    list_filter = ('tipo', 'data')
    search_fields = ('descricao', 'ordem_de_servico__id')
    date_hierarchy = 'data'

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'data_pagamento', 'valor_pago', 'forma_pagamento', 'numero_parcelas', 'data_vencimento')
    list_filter = ('forma_pagamento', 'data_pagamento')
    search_fields = ('pedido__id',)
    date_hierarchy = 'data_pagamento'