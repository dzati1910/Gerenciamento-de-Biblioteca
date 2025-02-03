from django.test import TestCase
from ..forms import CategoriaForm, CategoriaFormCommonUser, LivroForm, LivroFormCommonUser, UserLoginForm, UserRegisterForm
from ..models import Categoria, Livro
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CategoriaFormTestCase(TestCase):
    
    def test_categoria_form_valid(self):
        """Testa se o formulário da categoria é válido quando os dados são corretos."""
        form_data = {
            'nome': 'Ficção Científica',
            'descricao': 'Livros que exploram possibilidades científicas e tecnológicas.'
        }
        form = CategoriaForm(data=form_data)
        self.assertTrue(form.is_valid())  

    def test_categoria_form_invalid_nome_vazio(self):
        """Testa se o formulário da categoria é inválido quando o nome está vazio."""
        form_data = {
            'nome': '',
            'descricao': 'Descrição de categoria inválida.'
        }
        form = CategoriaForm(data=form_data)
        self.assertFalse(form.is_valid()) 
        self.assertIn('nome', form.errors) 

    def test_categoria_form_invalid_nome_duplicado(self):
        """Testa se o formulário da categoria é inválido quando o nome é duplicado."""
 
        Categoria.objects.create(nome='Ficção Científica', descricao='Livros de ficção científica.')

        form_data = {
            'nome': 'Ficção Científica', 
            'descricao': 'Outro livro de ficção científica.'
        }
        form = CategoriaForm(data=form_data)
        self.assertFalse(form.is_valid()) 
        self.assertIn('nome', form.errors) 

class LivroFormTestCase(TestCase):

    def setUp(self):
        """Configuração inicial: criação de categoria para os testes."""
        self.categoria_ficcao = Categoria.objects.create(
            nome='Ficção Científica',
            descricao='Livros sobre ciência e tecnologia.'
        )

    def test_livro_form_valid(self):
        """Testa se o formulário do livro é válido quando os dados são corretos."""
        form_data = {
            'titulo': 'O Guia do Mochileiro das Galáxias',
            'autor': 'Douglas Adams',
            'data_publicacao': now().date(),
            'isbn': '1234567890123',
            'categorias': [self.categoria_ficcao.id],  
            'copias_disponiveis': 5
        }
        form = LivroForm(data=form_data)
        self.assertTrue(form.is_valid())  

    def test_livro_form_invalid_isbn(self):
        """Testa se o formulário do livro é inválido com ISBN inválido."""
        form_data = {
            'titulo': 'O Guia do Mochileiro das Galáxias',
            'autor': 'Douglas Adams',
            'data_publicacao': now().date(),
            'isbn': '12345', 
            'categorias': [self.categoria_ficcao.id], 
            'copias_disponiveis': 5
        }
        form = LivroForm(data=form_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('isbn', form.errors)  

    def test_livro_form_invalid_copias_disponiveis_negativo(self):
        """Testa se o formulário do livro é inválido com cópias disponíveis negativas."""
        form_data = {
            'titulo': 'O Guia do Mochileiro das Galáxias',
            'autor': 'Douglas Adams',
            'data_publicacao': now().date(),
            'isbn': '1234567890123',
            'categorias': [self.categoria_ficcao.id], 
            'copias_disponiveis': -1  
        }
        form = LivroForm(data=form_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('copias_disponiveis', form.errors)  

    def test_livro_form_invalid_sem_categoria(self):
        """Testa se o formulário do livro é inválido quando não há categoria selecionada."""
        form_data = {
            'titulo': 'O Guia do Mochileiro das Galáxias',
            'autor': 'Douglas Adams',
            'data_publicacao': now().date(),
            'isbn': '1234567890123',
            'categorias': [],  
            'copias_disponiveis': 5
        }
        form = LivroForm(data=form_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('categorias', form.errors)  
        
class UserLoginFormTestCase(TestCase):
    
    def setUp(self):
        """Configuração inicial: criação de um usuário de teste."""
        self.user = get_user_model().objects.create_user(
            username='usuario_teste',
            password='senha_teste'
        )

    def test_login_form_valido(self):
        """Testa se o formulário de login é válido com dados corretos."""
        dados_formulario = {
            'username': 'usuario_teste',
            'password': 'senha_teste'
        }
        formulario = UserLoginForm(data=dados_formulario)
        self.assertTrue(formulario.is_valid())  

    def test_login_form_usuario_invalido(self):
        """Testa se o formulário de login é inválido com nome de usuário incorreto."""
        dados_formulario = {
            'username': 'usuario_inexistente',
            'password': 'senha_teste'
        }
        formulario = UserLoginForm(data=dados_formulario)
        self.assertFalse(formulario.is_valid())  
        self.assertIn('__all__', formulario.errors) 

    def test_login_form_senha_invalida(self):
        """Testa se o formulário de login é inválido com senha incorreta."""
        dados_formulario = {
            'username': 'usuario_teste',
            'password': 'senha_errada'
        }
        formulario = UserLoginForm(data=dados_formulario)
        self.assertFalse(formulario.is_valid())  
        self.assertIn('__all__', formulario.errors)  

        
class UserRegisterFormTestCase(TestCase):

    def test_register_form_valid(self):
        """Testa se o formulário de registro de usuário é válido com dados corretos."""
        form_data = {
            'username': 'novo_usuario',
            'email': 'novo@dominio.com',
            'password1': 'senha_segura123',
            'password2': 'senha_segura123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid()) 

    def test_register_form_invalid_password_mismatch(self):
        """Testa se o formulário de registro é inválido quando as senhas não coincidem."""
        form_data = {
            'username': 'novo_usuario',
            'email': 'novo@dominio.com',
            'password1': 'senha_segura123',
            'password2': 'senha_errada123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('password2', form.errors)  

    def test_register_form_invalid_email(self):
        """Testa se o formulário de registro é inválido quando o e-mail é inválido."""
        form_data = {
            'username': 'novo_usuario',
            'email': 'email_invalido',
            'password1': 'senha_segura123',
            'password2': 'senha_segura123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('email', form.errors)  

    def test_register_form_invalid_username_taken(self):
        """Testa se o formulário de registro é inválido quando o nome de usuário já está em uso."""

        get_user_model().objects.create_user(
            username='usuario_existente',
            password='senha_segura123'
        )

        form_data = {
            'username': 'usuario_existente', 
            'email': 'novo@dominio.com',
            'password1': 'senha_segura123',
            'password2': 'senha_segura123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('username', form.errors) 
        
class LivroFormCommonUserTest(TestCase):


    @classmethod
    def setUpTestData(cls):
        """
        Configuração inicial para criar instâncias de Livro para testes.
        """
        cls.livro = Livro.objects.create(
            titulo="Teste Livro",
            autor="Autor Teste",
            data_publicacao="2023-01-01",
            isbn="9783161484100",
            copias_disponiveis=5
        )

    def test_valid_form(self):
        """
        Testa se o formulário é válido com dados corretos.
        """
        data = {'copias_disponiveis': 3}
        form = LivroFormCommonUser(data=data, instance=self.livro)
        self.assertTrue(form.is_valid())

    def test_invalid_form_negative_copias(self):
        """
        Testa se o formulário é inválido com número negativo de cópias.
        """
        data = {'copias_disponiveis': -2}
        form = LivroFormCommonUser(data=data, instance=self.livro)
        self.assertFalse(form.is_valid())
        self.assertIn('copias_disponiveis', form.errors)

    def test_form_save(self):
        """
        Testa se o formulário salva corretamente as cópias disponíveis.
        """
        data = {'copias_disponiveis': 10}
        form = LivroFormCommonUser(data=data, instance=self.livro)
        self.assertTrue(form.is_valid())
        form.save()
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.copias_disponiveis, 10)


class CategoriaFormCommonUserTest(TestCase):


    @classmethod
    def setUpTestData(cls):
        """
        Configuração inicial para criar instâncias de Categoria para testes.
        """
        cls.categoria = Categoria.objects.create(
            nome="Teste Categoria",
            descricao="Categoria para testes"
        )

    def test_valid_form(self):
        """
        Testa se o formulário é válido com dados corretos.
        """
        data = {'nome': 'Nova Categoria'}
        form = CategoriaFormCommonUser(data=data, instance=self.categoria)
        self.assertTrue(form.is_valid())

    def test_invalid_form_empty_name(self):
        """
        Testa se o formulário é inválido com nome vazio.
        """
        data = {'nome': ''}
        form = CategoriaFormCommonUser(data=data, instance=self.categoria)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_form_save(self):
        """
        Testa se o formulário salva corretamente o nome da categoria.
        """
        data = {'nome': 'Categoria Atualizada'}
        form = CategoriaFormCommonUser(data=data, instance=self.categoria)
        self.assertTrue(form.is_valid())
        form.save()
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nome, 'Categoria Atualizada')
