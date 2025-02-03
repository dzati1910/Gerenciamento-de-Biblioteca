"""
models.py
Arquivo responsável pelos modelos da aplicação 'biblioteca'.
Define estrutura dos dados para Categorias, Livros e Empréstimos.
Inclui validações e lógica de negócios para controle de empréstimos.
"""

from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone   
from django.utils.timezone import now

# Modelo para Categorias
class Categoria(models.Model):
    """
    Modelo para representar categorias de livros.
    Campos:
        - nome: Nome da categoria (único, obrigatório).
        - descricao: Descrição da categoria (opcional).
    Validações:
        - O nome não pode ser vazio ou conter apenas espaços.
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nome

    def clean(self):
        """
        Validação customizada para o modelo Categoria.
        Verifica se o nome da categoria está preenchido corretamente.
        """
        super().clean()

        if not self.nome.strip():
            raise ValidationError("O nome da categoria não pode ser vazio ou conter apenas espaços.")

# Modelo para Livros
def validar_isbn(value):
    """
    Validador customizado para campo ISBN.
    Verifica se o valor contém apenas dígitos e possui 10 ou 13 caracteres.
    """
    if not value.isdigit() or len(value) not in (10, 13):
        raise ValidationError("ISBN deve conter 10 ou 13 caracteres.")

class Livro(models.Model):
    """
    Modelo para representar livros.
    Campos:
        - titulo: Título do livro (obrigatório).
        - autor: Autor do livro (obrigatório).
        - data_publicacao: Data de publicação do livro.
        - isbn: Número ISBN do livro (único, 10 ou 13 dígitos).
        - categorias: Relação ManyToMany com Categoria.
        - copias_disponiveis: Número de cópias disponíveis para empréstimo.
    Métodos:
        - emprestar(usuario): Registra empréstimo de livro para usuário.
    Validações:
        - Título e autor não podem ser vazios.
        - Número de cópias disponíveis não pode ser negativo.
    """
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    data_publicacao = models.DateField()
    isbn = models.CharField(
        max_length=13,
        unique=True,
        validators=[validar_isbn]
    )
    categorias = models.ManyToManyField(
        Categoria,
        related_name="livros",
        blank=False
    )
    copias_disponiveis = models.PositiveIntegerField(default=1)

    @transaction.atomic
    def emprestar(self, usuario):
        """
        Realiza empréstimo de livro para usuário.
        Usa transação para garantir consistência de dados.
        Args:
            usuario: Instância de User que está realizando o empréstimo.
        Raises:
            ValidationError: Se não houver cópias disponíveis.
        """
        livro = Livro.objects.select_for_update().get(pk=self.pk)
        if livro.copias_disponiveis > 0:
            Emprestimo.objects.create(livro=livro, usuario=usuario)
            livro.copias_disponiveis -= 1
            livro.save()
            usuario.save()
        else:
            raise ValidationError("Nenhuma cópia disponível.")
    def __str__(self):
        return self.titulo

    def clean(self):
        """
        Validação customizada para o modelo Livro.
        Verifica se título, autor e cópias disponíveis estão corretos.
        """
        super().clean()  
        
        if self.copias_disponiveis < 0:
            raise ValidationError("O número de cópias disponíveis não pode ser negativo.")

        if not self.titulo.strip():
            raise ValidationError("O título do livro não pode ser vazio.")

        if not self.autor.strip():
            raise ValidationError("O nome do autor não pode ser vazio.")

class Emprestimo(models.Model):
    """
    Modelo para representar empréstimos de livros.
    Campos:
        - usuario: Relação ForeignKey com User.
        - livro: Relação ForeignKey com Livro.
        - data_emprestimo: Data de realização do empréstimo.
        - data_devolucao: Data de devolução do livro (opcional).
        - devolvido: Indica se o livro foi devolvido.
    Métodos:
        - registrar_devolucao(): Marca empréstimo como devolvido e atualiza estoque.
    Validações:
        - Verifica existência de empréstimos ativos para mesmo usuário e livro.
        - Data de devolução não pode ser anterior à data de empréstimo.
        - Se devolvido, data de devolução deve estar preenchida.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="emprestimos"
    )
    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name="emprestimos"
    )
    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(blank=True, null=True)
    devolvido = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.livro.titulo}"
    
    def registrar_devolucao(self):
        """
        Registra devolução de livro.
        Atualiza status do empréstimo e incrementa cópias disponíveis do livro.
        """
        self.devolvido = True
        self.data_devolucao = now()
        self.save()
        self.livro.copias_disponiveis += 1
        self.livro.save()

    def clean(self):
        """
        Validação customizada para o modelo Emprestimo.
        Verifica regras de negócios para empréstimos e devoluções.
        """
        super().clean()
        
        emprestimo_existente = Emprestimo.objects.filter(
            usuario=self.usuario,
            livro=self.livro,
            devolvido=False
        ).exclude(pk=self.pk)

        if emprestimo_existente.exists():
            raise ValidationError("Este usuário já possui um empréstimo deste livro.")

        if self.data_devolucao and self.data_devolucao < self.data_emprestimo:
            raise ValidationError("A data de devolução não pode ser anterior à data do empréstimo.")
        
        if self.devolvido and not self.data_devolucao:
            raise ValidationError("Se o livro foi devolvido, a data de devolução deve ser informada.")
        
        if self.livro.copias_disponiveis <= 0:
            raise ValidationError("Não há cópias disponíveis para empréstimo.")
        
    class Meta:
        unique_together = ('usuario', 'livro', 'data_emprestimo')