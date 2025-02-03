from datetime import date
from django.test import TestCase, Client
from ..models import *
from ..forms import *
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.urls import reverse

# Tests Views Emprestimo

class EmprestimoTestCase(TestCase):
    
    def setUp(self):
        # Configuração inicial: criação de usuário e livro
        self.usuario = User.objects.create_user(username="usuario_teste", password="senha_teste")
        self.livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Autor Teste",
            data_publicacao=now(),
            isbn="1234567890123",
            copias_disponiveis=3
        )

    def test_registrar_emprestimo_sucesso(self):
        """Testa se um empréstimo é registrado corretamente."""
        emprestimo = Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=now(),
            devolvido=False
        )
        self.livro.copias_disponiveis -= 1
        self.livro.save()

        self.assertEqual(Emprestimo.objects.count(), 1)
        self.assertEqual(self.livro.copias_disponiveis, 2)


    def test_emprestimo_duplicado(self):
        """Testa se o sistema bloqueia empréstimos duplicados do mesmo livro para o mesmo usuário."""
        Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=now(),
            devolvido=False
        )

        emprestimo_duplicado = Emprestimo.objects.filter(
            usuario=self.usuario,
            livro=self.livro,
            devolvido=False
        ).exists()

        self.assertTrue(emprestimo_duplicado)

    def test_registrar_devolucao_sucesso(self):
        """Testa se a devolução de um livro é registrada corretamente."""
        emprestimo = Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=now(),
            devolvido=False
        )
        emprestimo.devolvido = True
        emprestimo.data_devolucao = now()
        emprestimo.save()

        self.livro.copias_disponiveis += 1
        self.livro.save()

        self.assertTrue(emprestimo.devolvido)
        self.assertIsNotNone(emprestimo.data_devolucao)
        self.assertEqual(self.livro.copias_disponiveis, 4)

    def test_devolucao_invalida(self):
        """Testa se o sistema bloqueia devoluções para livros não emprestados."""
        emprestimo = Emprestimo.objects.filter(
            usuario=self.usuario,
            livro=self.livro,
            devolvido=False
        ).first()

        self.assertIsNone(emprestimo)
        
        # ----------------!---------------- #
        
# Tests Views Categorias
        
class CategoriaViewsTestCase(TestCase):

    def setUp(self):
        # Cria um usuário para autenticação
        self.usuario = User.objects.create_user(username='usuario_teste', password='senha_teste')
        
        # Cria categorias para testar
        self.categoria = Categoria.objects.create(nome='Ficção', descricao='Livros de ficção')

        # Define as URLs para facilitar os testes
        self.listar_url = reverse('listar_categoria')
        self.adicionar_url = reverse('adicionar_categoria')
        self.atualizar_url = reverse('atualizar_categoria', kwargs={'categoria_id': self.categoria.pk})
        self.excluir_url = reverse('excluir_categoria', kwargs={'pk': self.categoria.pk})

    def test_listar_categoria(self):
        """Testa a view de listar categorias"""
        self.client.login(username='usuario_teste', password='senha_teste')  # Simula o login
        response = self.client.get(self.listar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listar_categoria.html')
        self.assertContains(response, 'Ficção')

    def test_adicionar_categoria_unauthenticated(self):
        """Testa a view de adicionar categoria para um usuário não autenticado"""
        response = self.client.get(self.adicionar_url)  # Realiza GET antes de tentar POST
        self.assertEqual(response.status_code, 302)  # Espera redirecionamento para login
        self.assertRedirects(response, f'/biblioteca/login/?next={self.adicionar_url}')

    def test_atualizar_categoria_unauthenticated(self):
        """Testa a view de atualizar categoria para um usuário não autenticado"""
        response = self.client.get(self.atualizar_url)
        self.assertEqual(response.status_code, 302)
        # Corrigido: usar self.atualizar_url no parâmetro next
        self.assertRedirects(response, f'/biblioteca/login/?next={self.atualizar_url}')

    def test_excluir_categoria_unauthenticated(self):
        """Testa a view de excluir categoria para um usuário não autenticado"""
        response = self.client.get(self.excluir_url)
        login_url = reverse('login')  # Use Django's reverse() for dynamic URLs
        expected_url = f"{login_url}?next={self.excluir_url}"   
        self.assertRedirects(response, expected_url)
            
        # ----------------!---------------- #
        
# Tests Views Livros
        
class LivroViewsTestCase(TestCase):
    client = Client(enforce_csrf_checks=False),
    def setUp(self):
        self.client = Client()
        # Create a user with password and staff/superuser permissions
        self.usuario = User.objects.create_user(
            username='TestUser',
            password='senha_teste',
            is_staff=True,
            is_superuser=True
        )
        # Log in the user explicitly
        self.client.login(username='TestUser', password='senha_teste')
        # Create other test objects
        self.categoria = Categoria.objects.create(nome='Teste')
        self.livro = Livro.objects.create(
            titulo='Exemplo de Livro',
            autor='Teste Autor',
            data_publicacao=date.today(),
            isbn='1234567890123',
            copias_disponiveis=3,
        )
        self.livro.categorias.add(self.categoria)
        
        self.listar_url = reverse("listar_livro")
        self.atualizar_url = reverse('atualizar_livro', kwargs={'livro_id': self.livro.pk})
        self.excluir_url = reverse("excluir_livro", args=[self.livro.id])
        self.adicionar_url = reverse("adicionar_livro")
        # URLs das views

    def test_listar_livro_autenticado(self):
        """
        Testa o acesso à view de listagem de livros por um usuário autenticado.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.listar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "listar_livro.html")
        self.assertContains(response, "Exemplo de Livro")

    def test_listar_livro_nao_autenticado(self):
        """
        Testa o acesso à view de listagem de livros por um usuário não autenticado.
        """
        response = self.client.get(self.listar_url)
        self.assertEqual(response.status_code, 200)

    def test_atualizar_livro_autenticado(self):
        """
        Testa a atualização de um livro por um usuário autenticado.
        """
        self.client.login(username="testuser", password="testpassword")
        nova_categoria1 = Categoria.objects.create(nome="Drama")
        # ... restante do código ...

    def test_atualizar_livro_nao_autenticado(self):
        """
        Testa a tentativa de atualização de livro por usuário não autenticado.
        """
        response = self.client.post(self.atualizar_url)
        self.assertEqual(response.status_code, 200)

    def test_excluir_livro_autenticado(self):
        """
        Testa a exclusão de um livro por usuário autenticado.
        """
        url = reverse('excluir_livro', args=[self.livro.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Livro.objects.filter(id=self.livro.id).exists())

    def test_excluir_livro_nao_autenticado(self):
        """
        Testa a tentativa de exclusão de livro por usuário não autenticado.
        """
        response = self.client.post(self.excluir_url)
        self.assertEqual(response.status_code, 302)

    def test_adicionar_livro_autenticado(self):
        """
        Testa a adição de um novo livro por usuário autenticado.
        """
        # Primeiro POST com dados parciais
        response = self.client.post(self.adicionar_url)
        # Login e segundo POST com dados completos
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.adicionar_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Livro.objects.filter(titulo="Novo Livro").exists())

    def test_adicionar_livro_nao_autenticado(self):
        """
        Testa a tentativa de adição de livro por usuário não autenticado.
        """
        self.client.logout()
        response = self.client.post(self.adicionar_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Livro.objects.filter(titulo="Novo Livro").exists())

        # ----------------!---------------- #
