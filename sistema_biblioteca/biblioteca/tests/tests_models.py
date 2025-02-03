from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from ..models import Categoria, Livro, Emprestimo
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

class CategoriaTestCase(TestCase):

    def test_nome_categoria_vazio(self):
        """Testa se a categoria não pode ser salva com nome vazio ou apenas espaços."""
        categoria = Categoria(nome='   ', descricao="Descrição válida")


        with self.assertRaises(ValidationError):
            categoria.clean()  
            categoria.save()   

    def test_nome_categoria_valido(self):
        """Testa se a categoria pode ser salva com um nome válido."""
        categoria = Categoria(nome="Ficção Científica", descricao="Livros de ficção científica.")


        categoria.clean() 
        categoria.save()   


        self.assertEqual(Categoria.objects.count(), 1)
        self.assertEqual(Categoria.objects.first().nome, "Ficção Científica")

    
    def test_nome_categoria_unico(self):
        """Testa se a categoria não pode ser salva com um nome duplicado."""
        # Criação da primeira categoria
        categoria1 = Categoria(nome="Ficção Científica", descricao="Livros de ficção científica.")
        categoria1.save()


        categoria2 = Categoria(nome="Ficção Científica", descricao="Outro livro de ficção científica.")

        with self.assertRaises(IntegrityError):
            categoria2.save()  
            
class LivroTestCase(TestCase):

    def setUp(self):
        """Configuração inicial: criação de uma categoria para o livro"""
        self.categoria = Categoria.objects.create(nome="Ficção", descricao="Livros de ficção")
        
        self.usuario = User.objects.create_user(
            username='teste123',
            password='batatadoce'
        )
    
    def test_livro_validacao_isbn_invalido(self):
        livro = Livro(
            isbn="123abc",
            titulo="Livro",
            autor="Autor",
            data_publicacao=timezone.now(),
        )
        with self.assertRaises(ValidationError) as cm:
            livro.full_clean()
     
        self.assertIn("ISBN deve conter 10 ou 13 caracteres.", str(cm.exception))


    def test_livro_validacao_isbn_valido(self):
        """Testa se o ISBN com 13 dígitos é aceito como válido."""
        livro_valido = Livro(
            titulo="Livro Teste",
            autor="Autor Teste",
            data_publicacao=timezone.now().date(),
            isbn="1234567890123", 
            copias_disponiveis=5
        )
        try:
            livro_valido.full_clean()  
        except ValidationError:
            self.fail("ValidationError inesperada foi levantada!")

    def test_livro_validacao_copias_disponiveis_negativo(self):
        """Testa se o número de cópias disponíveis não pode ser negativo."""
        livro_invalido = Livro(
            titulo="Livro Teste",
            autor="Autor Teste",
            data_publicacao=timezone.now().date(),
            isbn="1234567890123",
            copias_disponiveis=-1  
        )
        
        with self.assertRaises(ValidationError):
            livro_invalido.full_clean()  

    def test_livro_validacao_titulo_vazio(self):
        """Testa se o título do livro não pode ser vazio."""
        livro_invalido = Livro(
            titulo="  ",  
            autor="Autor Teste",
            data_publicacao=timezone.now().date(),
            isbn="1234567890123",
            copias_disponiveis=5
        )

        with self.assertRaises(ValidationError):
            livro_invalido.full_clean()

    def test_livro_validacao_autor_vazio(self):
        """Testa se o nome do autor não pode ser vazio."""
        livro_invalido = Livro(
            titulo="Livro Teste",
            autor="  ", 
            data_publicacao=timezone.now().date(),
            isbn="1234567890123",
            copias_disponiveis=5
        )

        with self.assertRaises(ValidationError):
            livro_invalido.full_clean() 

    def test_livro_salvar_com_categoria(self):
        """Testa se um livro pode ser salvo com uma categoria associada."""
        livro_valido = Livro.objects.create(
            titulo="Livro Teste",
            autor="Autor Teste",
            data_publicacao=timezone.now().date(),
            isbn="1234567890123",
            copias_disponiveis=5
        )
        
        livro_valido.categorias.add(self.categoria)
        
  
        self.assertIn(self.categoria, livro_valido.categorias.all())
        livro_valido.save()

    def test_livro_str(self):
        """Testa se a representação em string do livro está correta."""
        livro = Livro.objects.create(
        titulo="Teste",
        autor="Author",
        data_publicacao=timezone.now().date(),
        isbn="1234567890123",
        copias_disponiveis=2,
    )
        livro.categorias.add(Categoria.objects.create(nome="Teste"))
        self.assertEqual(str(livro), "Teste")  
    
    def test_emprestar_livro_com_copias_disponiveis(self):
        livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Author",
            data_publicacao=timezone.now().date(),
            isbn="1234567890123",
            copias_disponiveis=2,
        )
        livro.categorias.add(self.categoria)
        livro.emprestar(self.usuario)

        livro.refresh_from_db()
        self.assertEqual(livro.copias_disponiveis, 1)
        self.assertEqual(Emprestimo.objects.count(), 1)

    def test_emprestar_livro_sem_copias_disponiveis(self):
        livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Author",
            data_publicacao=timezone.now().date(),

            isbn="1234567890123",
            copias_disponiveis=0,
        )
        with self.assertRaises(ValidationError) as cm:
            livro.emprestar(self.usuario)
        self.assertIn("Nenhuma cópia disponível.", str(cm.exception))

        
class EmprestimoTestCase(TestCase):
    @override_settings(USE_TZ=True)
    
    def setUp(self):
        """Configuração inicial: criação de usuário, livro e categoria"""
        self.usuario = User.objects.create_user(username="usuario_teste", password="senha_teste")
        self.categoria = Categoria.objects.create(nome="Ficção", descricao="Livros de ficção")
        self.livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Autor Teste",
            data_publicacao=timezone.now().date(),
            isbn="1234567890123",
            copias_disponiveis=5
        )
        self.livro.categorias.add(self.categoria)

    @override_settings(USE_TZ=True)
    def test_emprestimo_data_devolucao_anterior(self):

        isbn = get_random_string(13, allowed_chars='0123456789')
        livro = Livro.objects.create(
            titulo="Livro Teste",
            autor="Author",
            data_publicacao=timezone.localdate(),
            isbn=isbn,
            copias_disponiveis=1,
        )
        user = User.objects.create_user(
            username="TestUser",
            password="senha_teste",
            is_staff=True,
            is_superuser=True
        )
        

        data_emprestimo = timezone.now()
        data_devolucao = data_emprestimo - timedelta(days=1)
        
        emprestimo = Emprestimo(
            usuario=user,
            livro=livro,
            data_emprestimo=data_emprestimo,
            data_devolucao=data_devolucao,
            devolvido=True
        )
        
        original_auto_now_add = emprestimo._meta.get_field('data_emprestimo').auto_now_add
        emprestimo._meta.get_field('data_emprestimo').auto_now_add = False
        
        with self.assertRaises(ValidationError) as cm:
            emprestimo.full_clean()
        

        self.assertIn("A data de devolução não pode ser anterior à data do empréstimo.", cm.exception.messages)

        emprestimo._meta.get_field('data_emprestimo').auto_now_add = original_auto_now_add


    def test_emprestimo_devolucao_sem_data(self):
        """Testa se a devolução precisa ter data quando o livro for marcado como devolvido."""
        emprestimo = Emprestimo(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=timezone.now().date(),
            devolvido=True  
        )
        

        with self.assertRaises(ValidationError):
            emprestimo.full_clean()  

    def test_emprestimo_sem_copias_disponiveis(self):
        """Testa se não é possível criar um empréstimo quando não há cópias disponíveis."""
        self.livro.copias_disponiveis = 0 
        self.livro.save()

        emprestimo = Emprestimo(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=timezone.now().date(),
            devolvido=False
        )
        
        with self.assertRaises(ValidationError):
            emprestimo.full_clean()  

    def test_emprestimo_unico_usuario_livro(self):

        Emprestimo.objects.create(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=timezone.now(),
            devolvido=False
        )

        new_emprestimo = Emprestimo(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=timezone.now(),
            devolvido=False
        )


        with self.assertRaises(ValidationError) as cm:
            new_emprestimo.full_clean()


        self.assertIn("Este usuário já possui um empréstimo deste livro.", str(cm.exception))

    def test_emprestimo_validacao_sucesso(self):
        """Testa se o empréstimo é criado corretamente com dados válidos."""
        emprestimo = Emprestimo(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=timezone.now().date(),
            devolvido=False
        )
        
        try:
            emprestimo.full_clean()  
            emprestimo.save()
        except ValidationError:
            self.fail("ValidationError inesperada foi levantada!")
        
 
        self.assertEqual(Emprestimo.objects.count(), 1)
        self.assertEqual(emprestimo.usuario, self.usuario)
        self.assertEqual(emprestimo.livro, self.livro)

    def test_emprestimo_str(self):
        """Testa se a representação em string do empréstimo está correta."""
        emprestimo = Emprestimo(
            usuario=self.usuario,
            livro=self.livro,
            data_emprestimo=timezone.now().date(),
            devolvido=False
        )
        self.assertEqual(str(emprestimo), f"{self.usuario.username} - {self.livro.titulo}")  
