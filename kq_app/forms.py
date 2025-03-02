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
    cliente = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'cliente-autocomplete'})
    )

    class Meta:
        model = Pedido
        fields = ['cliente', 'data_entrega', 'observacoes']
        widgets = {
            'data_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_cliente(self):
        cliente_nome = self.cleaned_data['cliente']
        try:
            cliente = Cliente.objects.get(nome=cliente_nome)
            return cliente
        except Cliente.DoesNotExist:
            raise forms.ValidationError("Cliente não encontrado.")

class OrdemDeServicoForm(forms.ModelForm):
    mockup = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = OrdemDeServico
        fields = ['produto', 'quantidade', 'observacoes', 'mockup']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

OrdemDeServicoFormSet = formset_factory(OrdemDeServicoForm, extra=1, can_delete=True)

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'codigo_barras', 'unidade_medida']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control'}),
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