from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from pathlib import Path
import markdown
import os


from django.http import JsonResponse # Necessário para o upload de imagens do TinyMCE
from django.core.files.storage import default_storage # Para gerenciar o salvamento de arquivos
from django.views.decorators.csrf import csrf_exempt # CUIDADO: Usar com cautela em produção
import bleach

from .forms import (
    NoticiaForm, 
    ArquivosForm, 
    ArquivoFormSet, 
    ComentarioForm, 
    RespostaForm
    )
from .models import (
    Noticia, 
    ArquivoNaNoticia, 
    ComentarioNaNoticia
    )
from base.models import Perfil




@login_required(login_url='/login')
def NoticiaPublicar(request):
    if request.method == 'POST':
        noticia_form = NoticiaForm(request.POST, request.FILES)
        arquivo_form = ArquivosForm(request.POST, request.FILES)
            
        if noticia_form.is_valid() and arquivo_form.is_valid():
            noticia = noticia_form.save(commit=False)
            noticia.autor = request.user

            if noticia.corpo:
                # CORRIÇÃO AQUI: Converte frozenset para list antes de concatenar
                allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [ 
                    'img', 'video', 'source', 'iframe', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'blockquote', 'pre', 'code', 'table',
                    'thead', 'tbody', 'tr', 'th', 'td'
                ]
                allowed_attrs = {
                    **bleach.sanitizer.ALLOWED_ATTRIBUTES, 
                    'img': ['src', 'alt', 'width', 'height', 'style'],
                    'a': ['href', 'title', 'target', 'rel'],
                    'iframe': ['src', 'width', 'height', 'allowfullscreen', 'frameborder'],
                    'video': ['src', 'controls', 'width', 'height'],
                    'source': ['src', 'type'],
                    '*': ['style', 'class', 'id'], 
                }
                

                noticia.corpo = bleach.clean(
                    noticia.corpo,
                    tags=allowed_tags,
                    attributes=allowed_attrs,
                    strip=True
                )

            noticia.save()

            for arquivo in request.FILES.getlist('arquivos'):
                if arquivo:
                    ArquivoNaNoticia.objects.create(noticia=noticia, arquivos=arquivo)

            return redirect('feed')
    else:
        noticia_form = NoticiaForm()
        arquivo_form = ArquivosForm()
        
    context = {
        'arquivo_form':arquivo_form,
        'noticia_form':noticia_form,
        'minha_foto_de_perfil':Perfil.objects.get(user=request.user).foto_de_perfil
    }
    return render(request, "news/noticia_form.html", context)



@csrf_exempt # CUIDADO: Em produção, você DEVE implementar a proteção CSRF corretamente para requisições AJAX
@login_required(login_url='/login')
def upload_tinymce_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        img_file = request.FILES['file']
        # Define o caminho de upload dentro do seu MEDIA_ROOT
        # Ex: MEDIA_ROOT/uploads/news/editor_images/2025/06/imagem.jpg
        upload_dir = os.path.join('uploads', 'news', 'editor_images', timezone.now().strftime("%Y/%m/%d/"))
        
        # Garante que o diretório de upload exista
        full_upload_path = os.path.join(settings.MEDIA_ROOT, upload_dir)
        os.makedirs(full_upload_path, exist_ok=True)

        # Salva o arquivo usando o sistema de armazenamento padrão do Django
        file_path_in_media = default_storage.save(os.path.join(upload_dir, img_file.name), img_file)

        # Retorna a URL completa da imagem salva para o TinyMCE
        file_url = request.build_absolute_uri(default_storage.url(file_path_in_media))
        
        return JsonResponse({'location': file_url}) # TinyMCE espera uma resposta JSON com o campo 'location'
    return JsonResponse({'error': 'No image file uploaded'}, status=400)



def NoticiaPage(request, pk):
    if pk.isnumeric():
        noticia = get_object_or_404(Noticia, id=pk)
        arquivos = ArquivoNaNoticia.objects.filter(noticia=noticia)
        comentarios = ComentarioNaNoticia.objects.filter(noticia=noticia).order_by('-data')

        if noticia.visivel or ( not noticia.visivel and request.user.is_staff):
            conteudo_html = noticia.corpo # Agora 'corpo' já é o HTML
            perfil = Perfil.objects.get(user=request.user) if request.user.is_authenticated else None

            if request.method == 'POST' and request.user.is_authenticated:
                if not perfil.pode_comentar:
                    return HttpResponse('<h1>Você está proibido de comentar</h1>')

                if 'pai' in request.POST and request.POST.get('pai'):  # É resposta
                    form = RespostaForm(request.POST)
                else:
                    form = ComentarioForm(request.POST)

                if form.is_valid():
                    comentario = form.save(commit=False)
                    comentario.autor = perfil
                    comentario.noticia = noticia
                    comentario.save()
                    return redirect('noticia', pk=pk)

            context = {
                'conteudo_html':conteudo_html,
                'noticia': noticia,
                'arquivos': arquivos,
                'comentarios': comentarios,
                'comentario_form': ComentarioForm(),
                'resposta_form': RespostaForm(),
                'minha_foto_de_perfil': perfil.foto_de_perfil if perfil else None,
                'perfil': perfil,
                'numero_de_comentarios': len(comentarios)
            }

            if not noticia.visivel:
                context['aviso'] = "Essa notícia não está visível para os usuários"

            return render(request, "news/noticia_page.html", context)
        else:
            return redirect('feed')

    elif pk == 'feed':
        noticias = Noticia.objects.all().order_by('-updated')
        perfil = Perfil.objects.get(user=request.user) if request.user.is_authenticated else None
        return render(request, "news/feed.html", {
            'noticias': noticias,
            'minha_foto_de_perfil': perfil.foto_de_perfil if perfil else None
        })
    else:
        return redirect('feed')
    
    
# news/views.py

# ... (suas importações e outras funções)

@login_required(login_url='/login')
def NoticiaEditar(request, pk):
    noticia = get_object_or_404(Noticia, id=pk)

    # Lógica de permissão: apenas staff OU o autor da notícia pode editar
    # Ajustei o comentário para refletir essa lógica comum
    if not request.user.is_staff and noticia.autor != request.user:
        return HttpResponse("<h1>Você não tem permissão para editar esta notícia!</h1>")

    if request.method == 'POST':
        noticia_form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        # O ArquivoFormSet gerencia os arquivos existentes e os marcados para exclusão.
        # Não precisamos de uma query separada aqui antes de validar/salvar.
        arquivos_formset = ArquivoFormSet(request.POST, request.FILES, queryset=ArquivoNaNoticia.objects.filter(noticia=noticia))

        if noticia_form.is_valid() and arquivos_formset.is_valid():
            noticia = noticia_form.save(commit=False)
            noticia.autor = request.user # Garante que o autor permaneça correto

            # --- Lógica de Sanitização do HTML do TinyMCE (MUITO IMPORTANTE) ---
            if noticia.corpo:
                # CORREÇÃO: Converte bleach.sanitizer.ALLOWED_TAGS (frozenset) para list antes de concatenar
                allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [ 
                    'img', 'video', 'source', 'iframe', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'blockquote', 'pre', 'code', 'table',
                    'thead', 'tbody', 'tr', 'th', 'td'
                ]
                allowed_attrs = {
                    **bleach.sanitizer.ALLOWED_ATTRIBUTES, 
                    'img': ['src', 'alt', 'width', 'height', 'style'],
                    'a': ['href', 'title', 'target', 'rel'],
                    'iframe': ['src', 'width', 'height', 'allowfullscreen', 'frameborder'],
                    'video': ['src', 'controls', 'width', 'height'],
                    'source': ['src', 'type'],
                    '*': ['style', 'class', 'id'], 
                }
    
                noticia.corpo = bleach.clean(
                    noticia.corpo,
                    tags=allowed_tags,
                    attributes=allowed_attrs,
                    strip=True
                )
          

            noticia.save() 

            
            arquivos_formset.save() 
            
        
            for obj in arquivos_formset.deleted_objects:
                try:
                   
                    if obj.arquivos: 
                        Path(obj.arquivos.path).unlink(missing_ok=True) 
                    obj.delete()  
                except Exception as e:
                    
                    print(f"Erro ao excluir o arquivo {obj.arquivos.name}: {e}")

           
            novos_arquivos = request.FILES.getlist('novos_arquivos')
            for arq in novos_arquivos:
      
                ArquivoNaNoticia.objects.create(noticia=noticia, arquivos=arq)
            
            return redirect('noticia', pk=noticia.id) 

    else:
      
        noticia_form = NoticiaForm(instance=noticia)
      
        arquivos_formset = ArquivoFormSet(queryset=ArquivoNaNoticia.objects.filter(noticia=noticia))

    # Obtenha a foto de perfil do usuário logado para o contexto
    foto_de_perfil = Perfil.objects.get(user=request.user).foto_de_perfil

    context = {
        'noticia_form': noticia_form,
        'arquivos_formset': arquivos_formset,
        'noticia': noticia,
        'minha_foto_de_perfil':foto_de_perfil
    }
    return render(request, "news/editar.html", context)



@login_required(login_url='/login')
def NoticiaExcluir(request, pk):
    noticia = get_object_or_404(Noticia, id=pk)

    if not request.user.is_staff: 
        return HttpResponse("<h1>Somente o autor pode alterar alguma coisa dessa notícia!</h1>")

    if request.method == 'POST':
        # Exclui arquivos relacionados à notícia (seus anexos)
        arquivos = ArquivoNaNoticia.objects.filter(noticia=noticia.id)
        for arquivo in arquivos:
            try:
                Path(arquivo.arquivos.path).unlink(missing_ok=True)
            except Exception as e:
                print(f"Erro ao excluir : {e}")
        arquivos.delete()
        
        
        if noticia.capa_noticia:
            Path(noticia.capa_noticia.path).unlink(missing_ok=True)
        

        noticia.delete()
        return redirect('feed')

    return render(request, "news/excluir.html", {
                                                'obj': noticia,
                                                'minha_foto_de_perfil':Perfil.objects.get(user=request.user).foto_de_perfil
                                                })




def Procurar(request):
    q = request.GET.get('pesquisa') if request.GET.get('pesquisa') is not None else ''
    numero_de_noticia = 0
    noticias = Noticia.objects.filter(visivel=True).filter(
    
        Q(título__icontains=q) | Q(corpo__icontains=q) 
    ).order_by('-updated')
    
    numero_de_noticia = noticias.count()
    if request.user.is_authenticated:  
        foto_de_perfil = Perfil.objects.get(user=request.user).foto_de_perfil
    else:
        foto_de_perfil = None

    context = {
        'noticias': noticias,
        'numero_de_noticia': numero_de_noticia,
        'minha_foto_de_perfil': foto_de_perfil,
        'termo': q, 
    }
    return render(request, "news/procurar.html", context)
