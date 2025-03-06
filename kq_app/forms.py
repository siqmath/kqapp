from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory
from .models import Cliente, Pedido, OrdemDeServico, Produto, Custo, Pagamento
import re

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'cpf_cnpj', 'endereco', 'equipe', 'cep']
        widgets = {
            'telefone': forms.TextInput(attrs={'data-mask': '(00) 00000-0000'}),
            'cep': forms.TextInput(attrs={'data-mask': '00000-000'}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'data_entrega', 'observacoes', 'frete']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'data_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class OrdemDeServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ['produto', 'preco_unitario', 'quantidade_digitada', 'cor_tecido', 'observacoes', 'mockup',
                  'pp_masculino', 'pp_feminino', 'p_masculino', 'p_feminino',
                  'm_masculino', 'm_feminino', 'g_masculino', 'g_feminino',
                  'gg_masculino', 'gg_feminino', 'xg_masculino', 'xg_feminino',
                  'esp_masculino', 'esp_feminino']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantidade_digitada': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cor_tecido': forms.TextInput(attrs={'class': 'form-control'}),  # Widget para cor_tecido
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mockup': forms.FileInput(attrs={'class': 'form-control'}),
            'pp_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'pp_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'p_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'p_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'm_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'm_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'g_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'g_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'gg_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'gg_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'xg_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'xg_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'esp_masculino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'esp_feminino': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

OrdemDeServicoFormSet = formset_factory(OrdemDeServicoForm, extra=1, can_delete=True)

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'material', 'rendimento', 'unidade_medida']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.TextInput(attrs={'class': 'form-control'}),
            'rendimento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidade_medida': forms.Select(attrs={'class': 'form-control'}),
        }

class CustoForm(forms.ModelForm):
    class Meta:
        model = Custo
        fields = ['descricao', 'valor', 'tipo']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['data_pagamento', 'valor_pago', 'forma_pagamento', 'observacoes', 'numero_parcelas', 'data_vencimento']
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pagamento': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'numero_parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }