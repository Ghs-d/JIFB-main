# news/urls.py

from django.urls import path
from . import views # Isso importa todas as funções de view do seu news/views.py

urlpatterns = [
    # URL para a página de publicação de notícias
    path('publicar/', views.NoticiaPublicar, name='publicar_noticia'),
    
    # URL para o endpoint de upload de imagens do TinyMCE (NOVA)
    # Esta URL será usada pelo JavaScript do TinyMCE para enviar as imagens.
    path('upload_image_tinymce/', views.upload_tinymce_image, name='upload_tinymce_image'),
    
    # URL para a página de visualização de uma única notícia (detalhes)
    # O <str:pk> captura o ID da notícia.
    path('<str:pk>/', views.NoticiaPage, name='noticia'),
    
    # URL para o feed de notícias (listagem de todas as notícias)
    # Esta é a URL que será acessada como 'noticias/feed/' (após a inclusão no projeto principal)
    path('feed/', views.NoticiaPage, name='feed'),
    
    # URL para a página de edição de uma notícia
    path('editar/<str:pk>/', views.NoticiaEditar, name='editar_noticia'),
    
    # URL para a funcionalidade de exclusão de uma notícia
    path('excluir/<str:pk>/', views.NoticiaExcluir, name='excluir_noticia'),
    
    # URL para a página de pesquisa de notícias
    path('procurar/', views.Procurar, name='procurar_noticia'),
]