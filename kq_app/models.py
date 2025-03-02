# models.py
from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Cliente")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cpf_cnpj = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")
    equipe = models.CharField(max_length=200, blank=True, null=True, verbose_name="Equipe")  # Novo campo
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")  # Novo campo

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']

    def __str__(self):
        return f"{self.id} - {self.nome}"

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('novo', 'Novo'),
        ('em_producao', 'Em Produção'),
        ('aguardando_aprovacao', 'Aguardando Aprovação'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    data_entrega = models.DateField(blank=True, null=True, verbose_name="Data de Entrega")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações", default="")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='novo', verbose_name="Status do Pedido")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Valor Total")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nome}"

class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto", default="nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição", default="descrição")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço", default=0)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código de Barras")
    unidade_medida = models.CharField(max_length=20, default='un', verbose_name="Unidade de Medida")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class OrdemDeServico(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, verbose_name="Pedido")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, verbose_name="Produto")
    quantidade = models.IntegerField(default=0, verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário", default=0)
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações", default="")
    data_conclusao = models.DateField(blank=True, null=True, verbose_name="Data de Conclusão")
    responsavel = models.CharField(max_length=100, blank=True, null=True, verbose_name="Responsável", default="")

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"

    def __str__(self):
        return f"OS {self.id} - {self.produto.nome}"

    def save(self, *args, **kwargs):
        # Garante que o preco_unitario seja igual ao preço do produto ao salvar
        self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)

class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, verbose_name="Produto")
    quantidade = models.IntegerField(default=0, verbose_name="Quantidade")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    localizacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localização", default="")

    class Meta:
        verbose_name = "Estoque"
        verbose_name_plural = "Estoques"

    def __str__(self):
        return f"Estoque de {self.produto.nome}"

class Custo(models.Model):
    ordem_de_servico = models.ForeignKey(OrdemDeServico, on_delete=models.CASCADE, verbose_name="Ordem de Serviço", default=1)  # Default para evitar o erro
    descricao = models.CharField(max_length=200, verbose_name="Descrição", default="Custo adicional")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateTimeField(default=timezone.now, verbose_name="Data")
    tipo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Custo", default="")

    class Meta:
        verbose_name = "Custo"
        verbose_name_plural = "Custos"

    def __str__(self):
        return self.descricao

class Pagamento(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, verbose_name="Pedido")
    data_pagamento = models.DateTimeField(default=timezone.now, verbose_name="Data de Pagamento")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago")
    forma_pagamento = models.CharField(max_length=50, verbose_name="Forma de Pagamento")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações", default="")
    numero_parcelas = models.IntegerField(default=1, verbose_name="Número de Parcelas")
    data_vencimento = models.DateField(blank=True, null=True, verbose_name="Data de Vencimento")

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return f"Pagamento de {self.valor_pago} em {self.data_pagamento}"