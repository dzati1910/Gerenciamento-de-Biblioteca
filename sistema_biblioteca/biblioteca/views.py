"""
views.py
Arquivo responsável pelas views da aplicação 'biblioteca'.
Contém lógica para gerenciamento de categorias, livros, empréstimos e autenticação.
"""

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse  
from .models import Categoria, Livro, Emprestimo
from .forms import CategoriaForm, LivroForm, UserRegisterForm, LivroFormCommonUser, CategoriaFormCommonUser
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.views.decorators.csrf import csrf_protect

# View Base
def pagina_inicial(request): 
    """
    View responsável pela página inicial do sistema.
    Não requer autenticação.
    """
    return render(request, 'pagina_inicial.html')

def restricted_view(request):
    """
    View para exibir página de restrição de acesso.
    Usada quando o usuário não está autenticado.
    """
    return render(request, 'restrito.html')

def custom_login(request):
    """
    View para autenticação personalizada.
    Processa formulário de login e redireciona para página inicial.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(pagina_inicial)
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

def custom_logout(request):
    """
    View para logout personalizado.
    Realiza logout do usuário e redireciona para página inicial.
    """
    logout(request)
    return redirect('pagina_inicial')

def registro(request):
    """
    View para cadastro de novos usuários.
    Utiliza formulário UserRegisterForm para validação.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Cadastro realizado com sucesso. Faça login para continuar.")
            return redirect('login')
        else:
            messages.error(request, "Erro ao realizar o cadastro.")
    else:
        form = UserRegisterForm()
    return render(request, 'registro.html', {'form': form})

@login_required
@csrf_protect
def perfil_usuario(request):
    """
    View para exibir perfil do usuário logado.
    Requer autenticação e proteção CSRF.
    """
    user = request.user
    return render(request, 'perfil_usuario.html', {'user': user})

# ----------------!---------------- #

# Views de Categoria
@login_required
@csrf_protect
def listar_categoria(request):
    """
    View para listar todas as categorias.
    Requer autenticação.
    """
    categorias = Categoria.objects.all()    
    return render(request, 'listar_categoria.html', {'categorias': categorias})

@login_required
@permission_required('app.add_categoria', raise_exception=True)
@csrf_protect
def adicionar_categoria(request):
    """
    View para adicionar nova categoria.
    Requer permissão 'app.add_categoria' e autenticação.
    """
    if request.method == 'POST':  
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categoria')  
    else: 
        form = CategoriaForm()  
    return render(request, 'adicionar_categoria.html', {'form': form})

@login_required
@permission_required('app.view_categoria', raise_exception=True) 
@csrf_protect
def atualizar_categoria(request, categoria_id):
    """
    View para atualizar categoria existente.
    Requer permissão 'app.view_categoria', autenticação e proteção CSRF.
    """
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    
    if request.method == 'POST':
        if request.user.is_superuser:
            form = CategoriaForm(request.POST, instance=categoria)
        else:
            form = CategoriaFormCommonUser(request.POST, instance=categoria)
        
        if form.is_valid():
            form.save()
            return redirect('listar_categoria')
    else:
        if request.user.is_superuser:
            form = CategoriaForm(instance=categoria)
        else:
            form = CategoriaFormCommonUser(instance=categoria)
    
    return render(request, 'atualizar_categoria.html', {'form': form, 'categoria': categoria})

@login_required
@permission_required('app.view_categoria', raise_exception=True)  
@csrf_protect
def detalhes_categoria(request, pk):
    """
    View para exibir detalhes de categoria.
    Requer permissão 'app.view_categoria', autenticação e proteção CSRF.
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    if not (request.user.has_perm('app.view_categoria') or request.user.is_superuser):
        return HttpResponseForbidden()

    return render(request, 'detalhes_categoria.html', {'categoria': categoria})

@login_required  
@permission_required('app.delete_categoria', raise_exception=True)  
@csrf_protect
def excluir_categoria(request, pk):
    """
    View para excluir categoria.
    Requer permissão 'app.delete_categoria', autenticação e proteção CSRF.
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return HttpResponseRedirect(reverse('listar_categoria'))
    if not (request.user.has_perm('app.delete_categoria') or request.user.is_superuser):
        return HttpResponseForbidden()

    return render(request, 'confirmar_deletar_categoria.html', {'categoria': categoria})

# ----------------!---------------- #

# Views de Livro
@login_required
@csrf_protect
def listar_livro(request):
    """
    View para listar todos os livros.
    Requer autenticação.
    """
    livros = Livro.objects.all()    
    return render(request, 'listar_livro.html', {'livros': livros})

@login_required
@csrf_protect
def atualizar_livro(request, livro_id):
    """
    View para atualizar livro existente.
    Requer autenticação.
    """
    livro = get_object_or_404(Livro, pk=livro_id)
    
    if request.method == 'POST':
        if request.user.is_superuser:
            form = LivroForm(request.POST, instance=livro)
        else:
            form = LivroFormCommonUser(request.POST, instance=livro)
        
        if form.is_valid():
            form.save()
            return redirect('listar_livro')
    else:
        if request.user.is_superuser:
            form = LivroForm(instance=livro)
        else:
            form = LivroFormCommonUser(instance=livro)
    
    return render(request, 'atualizar_livro.html', {'form': form, 'livro': livro})

@login_required
@permission_required('app.delete_livro', raise_exception=True)
@csrf_protect
def excluir_livro(request, livro_id):
    """
    View para excluir livro.
    Requer permissão 'app.delete_livro', autenticação e proteção CSRF.
    """
    livro = get_object_or_404(Livro, pk=livro_id)
    
    if request.method == 'POST':
        livro.delete()
        return redirect(reverse('listar_livro'))  

    if not (request.user.has_perm('app.delete_livro') or request.user.is_superuser):
        raise PermissionDenied

    return render(request, 'confirmar_deletar_livro.html', {'livro': livro})

@login_required
@permission_required('app.add_livro', raise_exception=True)
@csrf_protect
def adicionar_livro(request):
    """
    View para adicionar novo livro.
    Requer permissão 'app.add_livro', autenticação e proteção CSRF.
    """
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_livro')
    else:
        form = LivroForm()
    return render(request, 'adicionar_livro.html', {'form': form})

# ----------------!---------------- #

# Views de Empréstimo
@login_required
@csrf_protect
def registrar_emprestimo(request):
    """
    View para registrar empréstimo de livro.
    Realiza verificações de disponibilidade e autenticação.
    """
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        usuario_id = request.POST.get('usuario_id')
        livro = get_object_or_404(Livro, id=livro_id)
        usuario = get_object_or_404(User, id=usuario_id)

        emprestimo_existente = Emprestimo.objects.filter(
            usuario=usuario,
            livro=livro,
            devolvido=False
        ).exists()
        if emprestimo_existente:
            return render(request, 'emprestimo_indisponivel2.html', {'livro': livro})

        try:
            livro.emprestar(usuario)
            return redirect('listar_emprestimos')
        except ValidationError:
            return render(request, 'emprestimo_indisponivel.html', {'livro': livro})

    livros = Livro.objects.all()
    usuarios = User.objects.all()
    return render(request, 'registrar_emprestimo.html', {'livros': livros, 'usuarios': usuarios})

@login_required
@csrf_protect
def registrar_devolucao(request):
    """
    View para registrar devolução de livro.
    Verifica existência de empréstimo ativo e autenticação.
    """
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        usuario_id = request.POST.get('usuario_id')
        livro = get_object_or_404(Livro, id=livro_id)
        usuario = get_object_or_404(User, id=usuario_id)

        emprestimo = Emprestimo.objects.filter(
            usuario=usuario,
            livro=livro,
            devolvido=False,
        ).first()

        if not emprestimo:
            return render(request, 'devolucao_indisponivel.html', {'livro': livro, 'usuario': usuario})

        try:
            emprestimo.registrar_devolucao()
        except ValidationError:
            return render(request, 'devolucao_indisponivel.html', {'livro': livro, 'usuario': usuario})

        return redirect('listar_emprestimos')  
    else:
        livros = Livro.objects.all()
        usuarios = User.objects.all()
        return render(request, 'registrar_devolucao.html', {'livros': livros, 'usuarios': usuarios})

@login_required
@csrf_protect
def listar_emprestimos(request):
    """
    View para listar empréstimos com filtro opcional.
    Aplica filtros 'ativos' ou 'devolvidos' conforme parâmetro GET.
    """
    emprestimos = Emprestimo.objects.all()
    filtro = request.GET.get('filtro')
    if filtro == 'ativos':
        emprestimos = emprestimos.filter(devolvido=False)
    elif filtro == 'devolvidos':
        emprestimos = emprestimos.filter(devolvido=True)
    return render(request, 'listar_emprestimos.html', {'emprestimos': emprestimos})