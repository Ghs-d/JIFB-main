# news/urls.py

from django.urls import path
from . import views 

urlpatterns = [
  
    path('publicar/', views.NoticiaPublicar, name='publicar_noticia'),
    path('upload_image_tinymce/', views.upload_tinymce_image, name='upload_tinymce_image'),
    
    
    path('feed/', views.FeedNoticiasView, name='feed'), 
    
    path('meus-artigos/', views.MeusArtigos, name='meus_artigos'),
    
    path('editar/<str:pk>/', views.NoticiaEditar, name='editar_noticia'), 
    path('excluir/<str:pk>/', views.NoticiaExcluir, name='excluir_noticia'), 
    path('procurar/', views.Procurar, name='procurar_noticia'),

  
    path('<str:pk>/', views.NoticiaPage, name='noticia'), 
]