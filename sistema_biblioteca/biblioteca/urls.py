from django.urls import path
from .views import *
urlpatterns = [
    # Paths Base
    path('pagina_inicial/', pagina_inicial, name='pagina_inicial'),
    path('login/', custom_login, name='login'), 
    path('logout/', custom_logout, name='logout'),
    path('registro/', registro, name='registro'),
    path('perfil_usuario', perfil_usuario, name='perfil_usuario'),
    
    # Paths Categoria
    path('listar_categoria/', listar_categoria, name='listar_categoria'),
    path('adicionar_categoria/', adicionar_categoria, name='adicionar_categoria'),
    path('atualizar_categoria/<int:categoria_id>/', atualizar_categoria, name='atualizar_categoria'),
    path('excluir_categoria/<int:pk>/', excluir_categoria, name='excluir_categoria'),
    
    # Paths Livro
    path('listar_livro/', listar_livro, name='listar_livro'),
    path('atualizar_livro/<int:livro_id>/',atualizar_livro, name='atualizar_livro'),
    path('excluir_livro/<int:livro_id>/', excluir_livro, name='excluir_livro'),
    path('adicionar_livro/', adicionar_livro, name='adicionar_livro'),
    
    # Paths Empréstimo
    path('listar_emprestimos/', listar_emprestimos, name='listar_emprestimos'),
    path('registrar_emprestimo/', registrar_emprestimo, name='registrar_emprestimo'),
    path('registrar_devolucao/', registrar_devolucao, name='registrar_devolucao'), 
]
