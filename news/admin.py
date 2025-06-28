# news/admin.py

from django.contrib import admin
from .models import Noticia, ArquivoNaNoticia, ComentarioNaNoticia # Importa os modelos específicos
from django import forms # Importa forms para personalizar widgets

# Classe que personaliza o admin para o modelo Noticia
class NoticiaAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de notícias no painel Admin
    list_display = ('título', 'autor', 'visivel', 'created', 'updated')
    
    list_filter = ('visivel', 'autor', 'created')
    
    
    search_fields = ('título', 'corpo', 'tags') 

    # Este método é usado para personalizar os widgets dos campos do modelo no Admin
    def formfield_for_dbfield(self, db_field, **kwargs):
       
        if db_field.name == 'corpo':
           
            kwargs['widget'] = forms.Textarea(attrs={'class': 'tinymce-editor', 'rows': 20, 'cols': 80})
        
        return super().formfield_for_dbfield(db_field, **kwargs)


# admin.site.register(ArquivoNaNoticia)
# admin.site.register(ComentarioNaNoticia)