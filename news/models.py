from django.contrib.auth.models import User
from base.models import Perfil
from django.db import models

# Create your models here.

class Noticia(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    título = models.CharField(max_length=500)
    
    corpo = models.TextField(blank=True, null=True) 
    capa_noticia = models.ImageField(upload_to="uploads/noticias/CAPAS/%Y/%m/%d")

   
    tags = models.CharField(max_length=255, blank=True, help_text="Separe as tags por vírgula")

    visivel = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.título

class ArquivoNaNoticia(models.Model):
    noticia = models.ForeignKey(Noticia, related_name='arquivos', on_delete=models.CASCADE)
    arquivos = models.FileField(upload_to="uploads/noticias/arquivos/", blank=True, null=True)

    def __str__(self):
        return f"Arquivo de {self.noticia.título}"


class ComentarioNaNoticia(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name="comentarios")
    pai = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="respostas")
    autor = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    comentario = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comentario[0:13] + "..." + "por" + " " + self.autor.user.username 

    