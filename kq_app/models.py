from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Cliente(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Cliente")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cpf_cnpj = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ")
    data_cadastro = models.DateTimeField(
        default=timezone.now, verbose_name="Data de Cadastro")
    equipe = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Equipe")
    cep = models.CharField(max_length=9, blank=True,
                           null=True, verbose_name="CEP")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    STATUS_CHOICES = (
        ('analise', 'Análise'),
        ('aprovado', 'Aprovado'),
        ('compra', 'Compra'),
        ('corte', 'Corte'),
        ('personalizacao', 'Personalização'),
        ('costura', 'Costura'),
        ('embalagem', 'Embalagem'),
        ('enviado', 'Enviado'),
    )

    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_criacao = models.DateTimeField(
        default=timezone.now, verbose_name="Data de Criação")
    data_entrega = models.DateField(
        blank=True, null=True, verbose_name="Data de Entrega")
    observacoes = models.TextField(
        blank=True, null=True, verbose_name="Observações", default="")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='novo', verbose_name="Status do Pedido")
    valor_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, verbose_name="Valor Total")
    frete = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Frete")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nome}"


class Produto(models.Model):
    UNIDADE_CHOICES = [
        ('kg', 'Kilograma'),
        ('metro', 'Metro'),
    ]

    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    material = models.CharField(
        max_length=200, verbose_name="Material do Produto", default="Material")
    rendimento = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Rendimento", default=1)
    unidade_medida = models.CharField(
        max_length=10,
        choices=UNIDADE_CHOICES,
        default='kg',
        verbose_name="Unidade de Medida"
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class OrdemDeServico(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE,
                               verbose_name="Pedido", related_name='ordens_de_servico')
    numero_os = models.IntegerField(
        verbose_name="Número da OS", blank=True, null=True)
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, verbose_name="Produto")
    preco_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Preço Unitário", default=0.00)
    observacoes = models.TextField(
        blank=True, null=True, verbose_name="Observações", default="")
    mockup = CloudinaryField('mockup', folder='mockups',
                             blank=True, null=True, verbose_name="Mockup")
    quantidade_digitada = models.IntegerField(
        default=0, verbose_name="Quantidade Digitada")
    cor_tecido = models.CharField(
        max_length=255, verbose_name="Cor do Tecido", blank=True, null=True)  # Novo campo

    pp_masculino = models.IntegerField(default=0, verbose_name="PP Masculino")
    pp_feminino = models.IntegerField(default=0, verbose_name="PP Feminino")
    p_masculino = models.IntegerField(default=0, verbose_name="P Masculino")
    p_feminino = models.IntegerField(default=0, verbose_name="P Feminino")
    m_masculino = models.IntegerField(default=0, verbose_name="M Masculino")
    m_feminino = models.IntegerField(default=0, verbose_name="M Feminino")
    g_masculino = models.IntegerField(default=0, verbose_name="G Masculino")
    g_feminino = models.IntegerField(default=0, verbose_name="G Feminino")
    gg_masculino = models.IntegerField(default=0, verbose_name="GG Masculino")
    gg_feminino = models.IntegerField(default=0, verbose_name="GG Feminino")
    xg_masculino = models.IntegerField(default=0, verbose_name="XG Masculino")
    xg_feminino = models.IntegerField(default=0, verbose_name="XG Feminino")
    esp_masculino = models.IntegerField(
        default=0, verbose_name="ESP Masculino")
    esp_feminino = models.IntegerField(default=0, verbose_name="ESP Feminino")

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ['numero_os']

    def __str__(self):
        return f"OS {self.numero_os} - {self.produto.nome}"

    def save(self, *args, **kwargs):
        if not self.numero_os:
            # Obtém o número da última OS para este pedido
            ultima_os = OrdemDeServico.objects.filter(
                pedido=self.pedido).order_by('-numero_os').first()
            if ultima_os:
                self.numero_os = ultima_os.numero_os + 1
            else:
                self.numero_os = 1  # Primeira OS para este pedido
        super().save(*args, **kwargs)

    @property
    def quantidade(self):
        return (
            self.pp_masculino + self.pp_feminino +
            self.p_masculino + self.p_feminino +
            self.m_masculino + self.m_feminino +
            self.g_masculino + self.g_feminino +
            self.gg_masculino + self.gg_feminino +
            self.xg_masculino + self.xg_feminino +
            self.esp_masculino + self.esp_feminino
        )


class Estoque(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, verbose_name="Produto")
    quantidade = models.IntegerField(default=0, verbose_name="Quantidade")
    data_atualizacao = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização")
    localizacao = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Localização", default="")

    class Meta:
        verbose_name = "Estoque"
        verbose_name_plural = "Estoques"

    def __str__(self):
        return f"Estoque de {self.produto.nome}"


class Custo(models.Model):
    ordem_de_servico = models.ForeignKey(OrdemDeServico, on_delete=models.CASCADE,
                                         verbose_name="Ordem de Serviço", default=1)  # Default para evitar o erro
    descricao = models.CharField(
        max_length=200, verbose_name="Descrição", default="Custo adicional")
    valor = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateTimeField(default=timezone.now, verbose_name="Data")
    tipo = models.CharField(max_length=50, blank=True,
                            null=True, verbose_name="Tipo de Custo", default="")

    class Meta:
        verbose_name = "Custo"
        verbose_name_plural = "Custos"

    def __str__(self):
        return self.descricao


class Pagamento(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, verbose_name="Pedido")
    data_pagamento = models.DateTimeField(
        default=timezone.now, verbose_name="Data de Pagamento")
    valor_pago = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor Pago")
    forma_pagamento = models.CharField(
        max_length=50, verbose_name="Forma de Pagamento")
    observacoes = models.TextField(
        blank=True, null=True, verbose_name="Observações", default="")
    numero_parcelas = models.IntegerField(
        default=1, verbose_name="Número de Parcelas")
    data_vencimento = models.DateField(
        blank=True, null=True, verbose_name="Data de Vencimento")

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return f"Pagamento de {self.valor_pago} em {self.data_pagamento}"
