# news/admin.py

from django.contrib import admin
from .models import Noticia, ArquivoNaNoticia, ComentarioNaNoticia 
from django import forms 

# Classe que personaliza o admin para o modelo Noticia
class NoticiaAdmin(admin.ModelAdmin):
 
    list_display = ('título', 'autor', 'visivel', 'created', 'updated')
    
    list_filter = ('visivel', 'autor', 'created')
    
    
    search_fields = ('título', 'corpo', 'tags') 

  
    def formfield_for_dbfield(self, db_field, **kwargs):
       
        if db_field.name == 'corpo':
           
            kwargs['widget'] = forms.Textarea(attrs={'class': 'tinymce-editor', 'rows': 20, 'cols': 80})
        
        return super().formfield_for_dbfield(db_field, **kwargs)


