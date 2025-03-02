from django.contrib import admin
from .models import Cliente, TipoProduto, Material, Produto, Pedido, OrdemDeServico, Custo

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'email', 'telefone', 'cpf', 'rg')
    search_fields = ('nome', 'email', 'cpf', 'rg')

@admin.register(TipoProduto)
class TipoProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'material', 'rendimento')
    search_fields = ('tipo__nome', 'material__nome')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'data_pedido', 'status')
    list_filter = ('status',)
    search_fields = ('numero', 'cliente__nome')

@admin.register(OrdemDeServico)
class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'pedido', 'produto', 'cor', 'quantidade', 'valor', 'prazo')
    list_filter = ('pedido', 'produto', 'cor')
    search_fields = ('numero', 'descricao')

@admin.register(Custo)
class CustoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'tipo', 'valor', 'status_pagamento')
    list_filter = ('tipo', 'status_pagamento')
    search_fields = ('pedido__numero', 'tipo')