from django.contrib import admin

# Register your models here.
from .models import Perfil
from news.models import *


admin.site.register(Perfil)
admin.site.register(Noticia)
admin.site.register(ArquivoNaNoticia)
admin.site.register(ComentarioNaNoticia)
