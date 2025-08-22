from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from .views import (
    PokemonListView,
    PokemonCarouselView,
    PokemonDetailView,
    PokemonCompareView,
    TypeListView,
    PokemonBattleView,
    pokemon_moves,
    landing_page,
)

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('pokemons/', PokemonListView.as_view(), name='buscar_pokemons'),
    path('caroussel/', PokemonCarouselView.as_view(), name='carrossel_pokemons'),
    # path('pokemons/<type>/', PokemonTypeListView.as_view(), name='lista'),
    path('pokemons/<int:pk>/', PokemonDetailView.as_view(), name='detalhe_pokemon'),
    path('comparar/', PokemonCompareView.as_view(), name='comparar_pokemons'),
    path('api/types/', TypeListView.as_view(), name='type-list'),
    path('battle/', PokemonBattleView.as_view(), name='pokemon-battle'),
    path('api/pokemon/<str:pokemon_name>/moves/', pokemon_moves, name='pokemon-moves'),
]

if settings.DEBUG:  # Apenas para desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)