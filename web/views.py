import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views.generic import CreateView

from web.forms import *
from web.models import *
from web.utils import *

def home(request):
    noticias = obtener_noticias_videojuegos()

    videojuegos = Videojuego.objects.all().order_by('-rating')[:6]

    return render(request, 'home.html', {
        'noticias': noticias,
        'videojuegos': videojuegos,
    })

def game(request, pk):
    juego = get_object_or_404(Videojuego, pk=pk)
    reviews = Review.objects.filter(videojuego=juego)

    similares = juegos_similares(juego)

    next_url = request.GET.get("next", None)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            resenya = form.save(commit=False)
            resenya.usuario = request.user
            resenya.videojuego = juego
            resenya.save()

            next_url_post = request.POST.get("next", None)
            if next_url_post:
                return redirect(f"{reverse('game', args=[pk])}?next={next_url_post}")
            else:
                return redirect(reverse('game', args=[pk]))

    form = ReviewForm()

    return render(request, "game.html", {
        "juego": juego,
        "similares": similares,
        "reviews": reviews,
        "form": form,
        "next": next_url,
    })

def game_list(request):
    q = request.GET.get('q')  # Búsqueda por título
    page_number = request.GET.get('page')  # Página actual
    category = request.GET.get('category')

    videojuegos = Videojuego.objects.all().order_by('titulo')

    if q:
        videojuegos = videojuegos.filter(titulo__startswith=q)
    if category:
        videojuegos = videojuegos.filter(genero__nombre__icontains=category)

    paginator = Paginator(videojuegos, 20)
    page_obj = paginator.get_page(page_number)

    filtros_get = request.GET.copy()
    if 'page' in filtros_get:
        filtros_get.pop('page')

    context = {
        'page_obj': page_obj,
        'generos': Genero.objects.all(),
        'genero_actual': category,
        'filtros_get': f"category={category}&q={q}" if category or q else "",
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/partial_list.html', context)
    return render(request, 'game_list.html', context)


@login_required
def guardar_juego(request, pk):
    if request.method == "POST":
        juego = get_object_or_404(Videojuego, pk=pk)
        usuario = request.user

        usuario.juegos_guardados.add(juego)

        next_url = request.POST.get("next", None)  # Si no se pasa next, se queda como None

        if next_url:
            return redirect(f"{reverse('game', args=[pk])}?next={next_url}")
        else:
            return redirect(reverse('game', args=[pk]))
    else:
        return redirect('home')

@login_required
def quitar_juego(request, pk):
    if request.method == "POST":
        juego = get_object_or_404(Videojuego, pk=pk)
        usuario = request.user

        usuario.juegos_guardados.remove(juego)

        next_url = request.POST.get("next", None)  # Si no se pasa next, se queda como None

        if next_url:
            return redirect(f"{reverse('game', args=[pk])}?next={next_url}")
        else:
            return redirect(reverse('game', args=[pk]))
    else:
        return redirect('home')

class register_view(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "register.html"


@login_required
def pagina_perfil(request):
    user = request.user
    juegos_favoritos = user.juegos_guardados.all()
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('pagina_perfil')
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'perfil.html', {'form': form, 'juegos': juegos_favoritos})

@login_required
def eliminar_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    juego = review.videojuego
    next_url = request.POST.get("next", None)
    if review.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar esta reseña.")
        return redirect('home')  # cambia esto por tu vista principal

    review.delete()
    messages.success(request, "Reseña eliminada correctamente.")
    return redirect(f"{reverse('game', args=[juego.pk])}?next={next_url}")

@login_required
def editar_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    juego = review.videojuego
    next_url_post = request.POST.get("next", None)

    if review.usuario != request.user:
        messages.error(request, "No tienes permiso para editar esta reseña.")
        return redirect('home')  # cambia esto por tu vista principal

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()

            return redirect(f"{reverse('game', args=[juego.pk])}?next={next_url_post}")
        else:
            form = ReviewForm()

    return redirect(f"{reverse('game', args=[juego.pk])}?next={next_url_post}")
