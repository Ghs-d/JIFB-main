# news/urls.py

from django.urls import path
from . import views 

urlpatterns = [
    # URLs MAIS ESPECÍFICAS devem vir primeiro
    path('publicar/', views.NoticiaPublicar, name='publicar_noticia'),
    path('upload_image_tinymce/', views.upload_tinymce_image, name='upload_tinymce_image'),
    
    # MUDE ESTA LINHA: Aponta para a nova view dedicada ao feed
    path('feed/', views.FeedNoticiasView, name='feed'), 
    
    path('meus-artigos/', views.MeusArtigos, name='meus_artigos'),
    

    # URLs de edição e exclusão
    path('editar/<str:pk>/', views.NoticiaEditar, name='editar_noticia'), 
    path('excluir/<str:pk>/', views.NoticiaExcluir, name='excluir_noticia'), 
    path('procurar/', views.Procurar, name='procurar_noticia'),

    # URL CORINGA: Deve vir por último para não "capturar" as URLs fixas acima.
    path('<str:pk>/', views.NoticiaPage, name='noticia'), 
]