from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE
        )
    
    bio = models.TextField(blank=True, null=True)
    
    foto_de_perfil = models.ImageField(
        upload_to="uploads/perfis",
        blank=True
        )
    
    pode_comentar = models.BooleanField(
        default=True
        )
    
    pode_alterar_foto_de_perfil = models.BooleanField(
        default=True
        )
    
    verificado = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.username



    