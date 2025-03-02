from django.db import models, transaction, IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime

class Cliente(models.Model):
    numero = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nome = models.CharField(max_length=100, default='Nome não informado')
    email = models.EmailField(default='email@exemplo.com')
    telefone = models.CharField(max_length=20, default='0000000000')
    cpf = models.CharField(max_length=11, unique=True)
    rg = models.CharField(max_length=9, unique=True)
    cep = models.CharField(max_length=8, default='00000000')
    endereco_completo = models.CharField(max_length=100, default='Endereço não informado')

LEAD_CHOICES = [
    ('indicacao', 'Indicação'),
    ('instagram', 'Instagram'),
    ('anuncio', 'Anúncio'),
    ('recorrente', 'Recorrente'),
    ('naoinformado', 'Não Informado'),
]
lead = models.CharField(max_length=20, choices=LEAD_CHOICES, default='naoinformado')

def save(self, *args, **kwargs):
    if not self.numero:
        with transaction.atomic():
            last_client = Cliente.objects.select_for_update().order_by('id').last()
            self.numero = f"C{last_client.id + 1 if last_client else 1:05d}"
    super().save(*args, **kwargs)

def __str__(self):
    return self.nome
class TipoProduto(models.Model):
    nome = models.CharField(max_length=100)

def __str__(self):
    return self.nome
class Material(models.Model):
    nome = models.CharField(max_length=100)

def __str__(self):
    return self.nome
class Produto(models.Model):
    tipo = models.ForeignKey(TipoProduto, on_delete=models.CASCADE, default=1)
material = models.ForeignKey(Material, on_delete=models.CASCADE)
rendimento = models.DecimalField(max_digits=10, decimal_places=2)

def __str__(self):
    return f"{self.tipo.nome} - {self.material.nome} (Rendimento: {self.rendimento})"
class Pedido(models.Model):
    numero = models.CharField(max_length=50, unique=True, editable=False)
cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
data_pedido = models.DateTimeField(auto_now_add=True)

STATUS_CHOICES = [
    ('preparacao', 'Preparação'),
    ('compra', 'Compra'),
    ('corte', 'Corte'),
    ('personalizacao', 'Personalização'),
    ('costura', 'Costura'),
    ('embalagem', 'Embalagem'),
]
status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='preparacao')

def save(self, *args, **kwargs):
    if not self.numero:
        with transaction.atomic():
            last_order = Pedido.objects.select_for_update().order_by('id').last()
            if last_order:
                last_number = int(last_order.numero[1:].split('-')[0])  # Extrai apenas a parte numérica antes do sufixo
                new_number = f"P{last_number + 1:05d}"
            else:
                new_number = "P00001"

            # Adiciona um sufixo de timestamp para garantir unicidade adicional
            timestamp_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
            new_number = f"{new_number}-{timestamp_suffix}"
            
            if Pedido.objects.filter(numero=new_number).exists():
                raise ValidationError("Número de pedido duplicado. Tente novamente.")

            self.numero = new_number
    
    try:
        super().save(*args, **kwargs)
    except IntegrityError:
        raise ValidationError("Número de pedido duplicado. Tente novamente.")

def __str__(self):
    return f"Pedido {self.numero} - {self.cliente.nome}"
class OrdemDeServico(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='ordens_servico')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    numero = models.CharField(max_length=20, unique=True, null=True, blank=True)
    descricao = models.TextField(blank=True, null=True, default='')
    materia_prima = models.CharField(max_length=255, default='')
    cor = models.CharField(max_length=30, default='Indefinido')
    quantidade = models.IntegerField(default=0)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prazo = models.DateField(null=True, blank=True)

    pp_masculino = models.IntegerField(default=0)
    p_masculino = models.IntegerField(default=0)
    m_masculino = models.IntegerField(default=0)
    g_masculino = models.IntegerField(default=0)
    gg_masculino = models.IntegerField(default=0)
    xg_masculino = models.IntegerField(default=0)
    esp_masculino = models.IntegerField(default=0)

    pp_feminino = models.IntegerField(default=0)
    p_feminino = models.IntegerField(default=0)
    m_feminino = models.IntegerField(default=0)
    g_feminino = models.IntegerField(default=0)
    gg_feminino = models.IntegerField(default=0)
    xg_feminino = models.IntegerField(default=0)
    esp_feminino = models.IntegerField(default=0)

    bordado = models.BooleanField(default=False)
    estampa = models.BooleanField(default=False)

    compra = models.BooleanField(default=False)
    corte = models.BooleanField(default=False)
    arte = models.BooleanField(default=False)
    estampa_fase = models.BooleanField(default=False)
    impressao = models.BooleanField(default=False)
    costura = models.BooleanField(default=False)
    embalagem = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)

def save(self, *args, **kwargs):
    if not self.numero:
        with transaction.atomic():
            last_os = OrdemDeServico.objects.select_for_update().order_by('id').last()
            new_number = f"OS{last_os.id + 1 if last_os else 1:05d}"
            
            if OrdemDeServico.objects.filter(numero=new_number).exists():
                raise ValidationError("Número de ordem de serviço duplicado. Tente novamente.")

            self.numero = new_number
    super().save(*args, **kwargs)

def __str__(self):
    return f"Ordem de Serviço {self.numero} para Pedido {self.pedido.numero}"
class Custo(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='custos')

TIPO_CUSTO_CHOICES = [
    ('materia_prima', 'Matéria-prima'),
    ('estampador', 'Estampador'),
    ('estampa', 'Estampa'),
    ('bordado', 'Bordado'),
    ('costura', 'Costura'),
    ('transporte', 'Transporte'),
    ('frete', 'Frete'),
    ('sublimacao', 'Sublimação'),
    ('terceirizado', 'Terceirizado'),
    ('retrabalho', 'Retrabalho'),
    ('imposto', 'Imposto'),
    ('vendedor', 'Vendedor'),
]
tipo = models.CharField(max_length=15, choices=TIPO_CUSTO_CHOICES, default='materia_prima')
valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
data_vencimento = models.DateField(null=True, blank=True)

STATUS_PAGAMENTO_CHOICES = [
    ('pendente', 'Pendente'),
    ('pago', 'Pago'),
]
status_pagamento = models.CharField(max_length=10, choices=STATUS_PAGAMENTO_CHOICES, default='pendente')

def __str__(self):
    return f"{self.tipo} - Pedido {self.pedido.numero}"