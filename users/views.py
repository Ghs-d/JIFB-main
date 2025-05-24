from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from pathlib import Path

from .forms import EditarUserProfileForm
from base.models import Perfil
from news.views import ComentarioNaNoticia

# Create your views here.


def UserProfile(request, pk):
    usuario = User.objects.get(username=pk)

    perfil = Perfil.objects.get(user=usuario)
    foto_de_perfil = perfil.foto_de_perfil

    minha_foto_de_perfil = Perfil.objects.get(user=request.user) if request.user.is_authenticated else None

    context = {
        "usuario":usuario,
        "foto_de_perfil":foto_de_perfil,
        "minha_foto_de_perfil":minha_foto_de_perfil.foto_de_perfil,
        "perfil":perfil
    }
    return render(request, "users/profile_user.html", context)


@login_required(login_url='/login')
def EditarUserProfile(request, pk):
    usuario = User.objects.get(username=pk)

    if request.user.username != pk and not request.user.is_staff:
        return redirect('user', pk)

    perfil = Perfil.objects.get(user=usuario)
    
    minha_foto_de_perfil = Perfil.objects.get(user=request.user)

    if request.method == 'POST':
        profile_form = EditarUserProfileForm(request.POST, request.FILES)
        
        if profile_form.is_valid():
            perfil.bio = profile_form.cleaned_data['bio']
            if profile_form.cleaned_data['foto_de_perfil']:
                Path(perfil.foto_de_perfil.path).unlink(missing_ok=True)
                perfil.foto_de_perfil = profile_form.cleaned_data['foto_de_perfil']
            
            perfil.save()
            return redirect('user', pk)

    else:
        profile_form = EditarUserProfileForm(instance=perfil)
    context = {
        "profile_form":profile_form,
        "minha_foto_de_perfil":minha_foto_de_perfil.foto_de_perfil,
    }
    return render(request, "users/editar_profile.html", context)

@login_required(login_url='/login')
def BloquearPerfil(request, pk):
    if request.user.is_staff:
        perfil = Perfil.objects.get(id=pk)
        if perfil.pode_comentar:
            perfil.pode_comentar = False
            perfil.save()
        else:
            perfil.pode_comentar = True
            perfil.save()
        return HttpResponse("<h1>Operação concluída com sucesso</h1>")
    else:
        return redirect('home')


@login_required(login_url='/login')
def ApagarComentariosUserProfile(request, pk):
    if request.user.is_staff:
        perfil = Perfil.objects.get(id=pk)
        perfil.pode_comentar = False
        perfil.save()
        comentarios = list(ComentarioNaNoticia.objects.filter(autor=perfil))
        for comentario in comentarios:
            comentario.delete()
        return HttpResponse("<h1>Operação concluída com sucesso</h1>")
    else:
        return redirect('home')
    
@login_required(login_url='/login')
def ExcluirComentario(request, pk):
    if request.user.is_staff:
        comentario = ComentarioNaNoticia.objects.get(id=pk)
        comentario.delete()
        return HttpResponse("<h1>Operação concluída com sucesso</h1>")
    else:
        return redirect('home')
