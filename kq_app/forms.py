# kq_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Cliente, Pedido, OrdemDeServico, Produto, QuantidadeTamanho
import re

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nome', 'email', 'telefone', 'cpf', 'rg',
            'cep', 'endereco_completo', 'lead'
        ]
        widgets = {
            'cep': forms.TextInput(attrs={'data-mask': '00000-000'}),
            'telefone': forms.TextInput(attrs={'data-mask': '(00) 00000-0000'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf').replace('.', '').replace('-', '')
        
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValidationError(_('CPF inválido. Deve conter 11 dígitos.'))
        
        # Validação do dígito verificador
        def calcula_digito(digs):
            soma = 0
            mult = len(digs) + 1
            for d in digs:
                soma += int(d) * mult
                mult -= 1
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        if cpf == cpf[0] * 11:
            raise ValidationError(_('CPF inválido.'))
        
        dig1 = calcula_digito(cpf[:9])
        dig2 = calcula_digito(cpf[:10])
        
        if not (int(cpf[9]) == dig1 and int(cpf[10]) == dig2):
            raise ValidationError(_('CPF inválido.'))
        
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(regex, email):
                raise ValidationError(_('Formato de e-mail inválido.'))
            
            if Cliente.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError(_('Este e-mail já está cadastrado.'))
            
        return email

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'status']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'select2'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class QuantidadeTamanhoForm(forms.ModelForm):
    class Meta:
        model = QuantidadeTamanho
        fields = ['genero', 'tamanho', 'quantidade']
        widgets = {
            'genero': forms.Select(choices=[
                ('', _('Selecione o gênero')),
                ('Masculino', _('Masculino')),
                ('Feminino', _('Feminino'))
            ], attrs={'class': 'form-control'}),
            
            'tamanho': forms.Select(
                choices=QuantidadeTamanho.TAMANHO_CHOICES,
                attrs={'class': 'form-control'}
            ),
            
            'quantidade': forms.NumberInput(attrs={
                'min': 0,
                'class': 'form-control',
                'placeholder': _('Qtd')
            })
        }

QuantidadeTamanhoFormSet = forms.inlineformset_factory(
    OrdemDeServico,
    QuantidadeTamanho,
    form=QuantidadeTamanhoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=20
)

class OrdemDeServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ['produto', 'materia_prima', 'descricao', 
                 'cor', 'valor', 'prazo', 'estado_atual']
        
        widgets = {
            'produto': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': _('Selecione um produto')
            }),
            
            'materia_prima': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ex: Malha PV 180g')
            }),
            
            'descricao': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Detalhes da produção...')
            }),
            
            'cor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ex: Vermelho Ferrari')
            }),
            
            'valor': forms.NumberInput(attrs={
                'step': 0.01,
                'min': 0,
                'class': "form-control",
                "placeholder": "R$"
             }),
             
             "prazo": forms.DateInput(
                 format=('%Y-%m-%d'),
                 attrs={
                     "type": "date",
                     "class": "form-control"
                 }
             ),
             
             "estado_atual": forms.Select(
                 attrs={"class": "form-control"}
             )
         }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor <= 0:
            raise ValidationError(_('O valor deve ser maior que zero.'))
        return valor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra produtos ativos se necessário
        self.fields['produto'].queryset = Produto.objects.all()