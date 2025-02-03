"""
forms.py
Arquivo responsável pelos formulários da aplicação 'biblioteca'.
Define formulários para categorias, livros e autenticação de usuários.
Inclui customizações de widgets, validações e melhorias conforme as recomendações Django.
"""

from django import forms
from .models import Categoria, Livro
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class CategoriaForm(forms.ModelForm):
    """
    Formulário para criação e atualização de categorias.
    Campos:
        - nome: Campo de texto para o nome da categoria.
        - descricao: Campo de texto para a descrição da categoria.
    Widget Customizados:
        - Nenhum, mantém os widgets padrão do Django.
    """
    nome = forms.CharField(
        max_length=100,
        help_text="Digite um nome para a categoria. Não pode conter apenas espaços."
    )
    descricao = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Adicione uma descrição opcional para a categoria."
    )
    
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']

class LivroForm(forms.ModelForm):
    """
    Formulário para criação e atualização de livros.
    Campos:
        - titulo: Título do livro.
        - autor: Autor do livro.
        - data_publicacao: Data de publicação do livro.
        - isbn: Número ISBN do livro.
        - categorias: Relação ManyToMany com Categoria.
        - copias_disponiveis: Número de cópias disponíveis.
    """
    titulo = forms.CharField(
        max_length=200,
        help_text="Título completo do livro. Não pode estar vazio."
    )
    autor = forms.CharField(
        max_length=100,
        help_text="Nome completo do autor. Não pode estar vazio."
    )
    data_publicacao = forms.DateField(
        help_text="Data de publicação no formato DD/MM/AAAA."
    )
    isbn = forms.CharField(
        max_length=13,
        help_text="Número ISBN de 10 ou 13 dígitos. Exemplo: 978-3-16-148410-0"
    )
    copias_disponiveis = forms.IntegerField(
        min_value=0,
        help_text="Número de cópias disponíveis. Não pode ser negativo."
    )

    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'data_publicacao', 'isbn', 'categorias', 'copias_disponiveis']
        labels = {
            'titulo': 'Título',
            'autor': 'Autor',
            'data_publicacao': 'Data de Publicação',
            'isbn': "ISBN de 13 dígitos",
            'categorias': 'Categorias',
            'copias_disponiveis': 'Cópias Disponíveis',
        }
        widgets = {
            'categorias': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'data_publicacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'copias_disponiveis': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class LivroFormCommonUser(forms.ModelForm):
    """
    Formulário simplificado para usuários comuns atualizar livros.
    Campos:
        - copias_disponiveis: Número de cópias disponíveis.
    """
    copias_disponiveis = forms.IntegerField(
        min_value=0,
        help_text="Número de cópias disponíveis. Não pode ser negativo."
    )

    class Meta:
        model = Livro
        fields = ['copias_disponiveis']

class CategoriaFormCommonUser(forms.ModelForm):
    """
    Formulário simplificado para usuários comuns atualizar categorias.
    Campos:
        - nome: Nome da categoria.
    """
    nome = forms.CharField(
        max_length=100,
        help_text="Digite um nome para a categoria. Não pode conter apenas espaços."
    )

    class Meta:
        model = Categoria
        fields = ['nome']

class UserLoginForm(AuthenticationForm):
    """
    Formulário de login personalizado.
    Campos:
        - username: Nome de usuário.
        - password: Senha do usuário.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuário'}),
        help_text="Digite seu nome de usuário registrado."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'}),
        help_text="Digite sua senha registrada."
    )

class UserRegisterForm(UserCreationForm):
    """
    Formulário de registro de usuários personalizado.
    Campos:
        - username: Nome de usuário.
        - email: Email do usuário.
        - password1: Senha do usuário.
        - password2: Confirmação de senha.
    """
    email = forms.EmailField(
        required=True,
        help_text="Digite um endereço de email válido."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']