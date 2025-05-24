from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from pathlib import Path
import markdown
import os

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

             # Lê o conteúdo Markdown do arquivo enviado
            # Primeiro, salve a notícia com o arquivo markdown
            noticia.save()

            # Agora leia o conteúdo do arquivo markdown enviado
            if noticia.corpo:
                markdown_file = noticia.corpo

                # Abrir o arquivo salvo no servidor
                with markdown_file.open(mode='rb') as f:
                    markdown_content = f.read().decode('utf-8')

                # Converte para HTML
                html_content = markdown.markdown(markdown_content)

                # Gera caminho do arquivo HTML com base na data/hora
                now = timezone.now()
                file_name = now.strftime("%Y-%m-%d_%H-%M-%S") + ".html"
                html_path = os.path.join("uploads", "noticias", "html", now.strftime("%Y/%m/%d/"))
                full_path = os.path.join(settings.MEDIA_ROOT, html_path)
                os.makedirs(full_path, exist_ok=True)

                full_file_path = os.path.join(full_path, file_name)
                relative_file_path = os.path.join(html_path, file_name)

                # Salva o conteúdo HTML em um novo arquivo
                with open(full_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)

                # Atualiza o campo corpo com o caminho do HTML gerado
                noticia.corpo.name = relative_file_path
                noticia.save()

            # Salva arquivos adicionais, se existirem
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




def NoticiaPage(request, pk):
    if pk.isnumeric():
        noticia = get_object_or_404(Noticia, id=pk)
        arquivos = ArquivoNaNoticia.objects.filter(noticia=noticia)
        comentarios = ComentarioNaNoticia.objects.filter(noticia=noticia).order_by('-data')

        if noticia.visivel or ( not noticia.visivel and request.user.is_staff):
            conteudo_html = noticia.corpo
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
    
    
@login_required(login_url='/login')
def NoticiaEditar(request, pk):

    noticia = Noticia.objects.get(id=pk)

    if not request.user.is_staff:
        return HttpResponse("<h1>Somente o autor pode alterar alguma coisa dessa notícia!</h1>")


    if request.method == 'POST':

        noticia_form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        arquivos_formset = ArquivoFormSet(request.POST, request.FILES, queryset=ArquivoNaNoticia.objects.filter(noticia=noticia))
        arquivos = ArquivoNaNoticia.objects.filter(noticia=noticia)


        if noticia_form.is_valid() and arquivos_formset.is_valid():
            noticia = noticia_form.save(commit=False)
            noticia.autor = request.user
            arquivos = arquivos_formset.save(commit=False)
            noticia_form.save()
            
            if noticia.corpo:
                markdown_file = noticia.corpo

                # Abrir o arquivo salvo no servidor
                with markdown_file.open(mode='rb') as f:
                    markdown_content = f.read().decode('utf-8')

                # Converte para HTML
                html_content = markdown.markdown(markdown_content)

                # Gera caminho do arquivo HTML com base na data/hora
                now = timezone.now()
                file_name = now.strftime("%Y-%m-%d_%H-%M-%S") + ".html"
                html_path = os.path.join("uploads", "noticias", "html", now.strftime("%Y/%m/%d/"))
                full_path = os.path.join(settings.MEDIA_ROOT, html_path)
                os.makedirs(full_path, exist_ok=True)

                full_file_path = os.path.join(full_path, file_name)
                relative_file_path = os.path.join(html_path, file_name)

                # Salva o conteúdo HTML em um novo arquivo
                with open(full_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)

                # Atualiza o campo corpo com o caminho do HTML gerado
                noticia.corpo.name = relative_file_path
                noticia.save()

            # Esse loop vai salvar os arquivos editados
            for arquivo in arquivos:
                arquivo.noticia = noticia
                arquivo.save()
            
            
            # Esse loop vai deletar os arquivos
            for obj in arquivos_formset.deleted_objects:
                arquivos = ArquivoNaNoticia.objects.filter(noticia=obj.noticia)

                for arquivo in arquivos:
                    try:
                        Path(arquivo.arquivos.path).unlink(missing_ok=True)  # apaga do disco
                        arquivo.delete()  # apaga do banco
                    except Exception as e:
                        print(f"Erro ao excluir {arquivo.arquivos.name}: {e}")

                obj.delete()  

                
            novos_arquivos = request.FILES.getlist('novos_arquivos')
            
            # Esse loop vai criar novos Arquivos
            for arq in novos_arquivos:
                ArquivoNaNoticia.objects.create(noticia=noticia, arquivos=arq)
            
            return redirect('home')

    else:
        noticia_form = NoticiaForm(instance=noticia)
        arquivos_formset = ArquivoFormSet(queryset=ArquivoNaNoticia.objects.filter(noticia=noticia))

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
    noticia = Noticia.objects.get(id=pk)

    if not request.user.is_staff:
        return HttpResponse("<h1>Somente o autor pode alterar alguma coisa dessa notícia!</h1>")

    if request.method == 'POST':
        # Exclui arquivos relacionados à notícia
        arquivos = ArquivoNaNoticia.objects.filter(noticia=noticia.id)
        for arquivo in arquivos:
            try:
                Path(arquivo.arquivos.path).unlink(missing_ok=True)
            except Exception as e:
                print(f"Erro ao excluir : {e}")
        arquivos.delete()
        
        
        # Exclui possíveis arquivos diretos da notícia
        if noticia.capa_noticia:
            Path(noticia.capa_noticia.path).unlink(missing_ok=True)
        if noticia.corpo:
            Path(noticia.corpo.path).unlink(missing_ok=True)

        noticia.delete()
        return redirect('feed')

    return render(request, "news/excluir.html", {
                                                'obj': noticia,
                                                'minha_foto_de_perfil':Perfil.objects.get(user=request.user).foto_de_perfil
                                                })


def Procurar(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    número_de_notícia = 0
    noticias = Noticia.objects.all().order_by('-updated').filter(
        Q(título__icontains=q) &
        Q(visivel=True)
        )
    número_de_notícia = noticias.count()
    if request.user.is_authenticated:  
        foto_de_perfil = Perfil.objects.get(user=request.user).foto_de_perfil
    else:
        foto_de_perfil = None
    context = {
        'noticias':noticias,    
        'número_de_notícia':número_de_notícia,
        'minha_foto_de_perfil':foto_de_perfil
    }
    return render(request, "news/procurar.html", context)