from django.shortcuts import get_object_or_404
from .models import Pokemon, Type, Move
from django.views.generic import ListView, DetailView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializers import TypeSerializer
from django.http import JsonResponse

TYPE_COLORS = {
    'normal': '#A8A878',
    'fire': '#F08030',
    'water': '#6890F0',
    'electric': '#F8D030',
    'grass': '#78C850',
    'ice': '#98D8D8',
    'fighting': '#C03028',
    'poison': '#A040A0',
    'ground': '#E0C068',
    'flying': '#A890F0',
    'psychic': '#F85888',
    'bug': '#A8B820',
    'rock': '#B8A038',
    'ghost': '#705898',
    'dragon': '#7038F8',
    'dark': '#705848',
    'steel': '#B8B8D0',
    'fairy': '#EE99AC',
}

def pokemon_moves(request, pokemon_name):
    try:
        pokemon = Pokemon.objects.get(name__iexact=pokemon_name)
        moves = pokemon.moves.all()  # Supondo que o modelo Pokemon tem uma relação ManyToMany com Move
        moves_data = [{"name": move.name} for move in moves]
        return JsonResponse(moves_data, safe=False)
    except Pokemon.DoesNotExist:
        return JsonResponse({"error": "Pokémon não encontrado"}, status=404)

class PokemonListView(ListView):
    model = Pokemon
    template_name = 'pokedex/lista.html'
    context_object_name = 'pokemons'
    paginate_by = 21  # Número de Pokémon por página

    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        type_name = self.request.GET.get('type', '').strip()
        if type_name:
            pokemon_type = get_object_or_404(Type, name=type_name)
            pokemon_type1 = Pokemon.objects.filter(primary_type=pokemon_type)
            pokemon_type2 = Pokemon.objects.filter(secondary_type=pokemon_type)
            if pokemon_type1.exists() and pokemon_type2.exists():
                return pokemon_type1 | pokemon_type2
            elif pokemon_type1.exists():
                return pokemon_type1
            elif pokemon_type2.exists():
                return pokemon_type2
            else:
                return Pokemon.objects.none()
        if query:
            if query.isdigit():
                return Pokemon.objects.filter(id=query)
            return Pokemon.objects.filter(name__icontains=query)
        return Pokemon.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_colors'] = TYPE_COLORS
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'json':
            pokemons = context['pokemons']
            data = {
                'pokemons': [
                    {
                        'id': pokemon.id,
                        'name': pokemon.name,
                        'hp': pokemon.hp,
                        'image_url': pokemon.image.url if pokemon.image else pokemon.image_url,
                        'primary_type': pokemon.primary_type.name if pokemon.primary_type else None,
                        'secondary_type': pokemon.secondary_type.name if pokemon.secondary_type else None,
                        'attack': pokemon.attack,
                        'defense': pokemon.defense,
                        'speed': pokemon.speed,
                        'card_style': pokemon.card_style,
                    }
                    for pokemon in pokemons
                ],
                'has_next': context['page_obj'].has_next()
            }
            return JsonResponse(data)
        return super().render_to_response(context, **response_kwargs)


class PokemonCarouselView(PokemonListView):
    template_name = 'pokedex/carrossel.html'
    context_object_name = 'pokemons'
    paginate_by = 10  # Número de Pokémon por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']  # Obtém o paginator do contexto
        context['pages'] = [
            paginator.page(page_num).object_list for page_num in paginator.page_range
        ]  # Lista de objetos por página
        return context  # Limita a 10 Pokémon para o carrossel


class PokemonDetailView(DetailView):
    model = Pokemon
    template_name = 'pokedex/detalhe.html'
    context_object_name = 'pokemon'


class PokemonCompareView(ListView):
    model = Pokemon
    template_name = 'pokedex/comparar.html'
    context_object_name = 'all_pokemons'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pokemon1_query = self.request.GET.get('pokemon1')
        pokemon2_query = self.request.GET.get('pokemon2')

        default_image_url = '/static/pokedex/images/default.jpg'
        
        if pokemon1_query:
            if pokemon1_query.isdigit():
                context['pokemon1'] = Pokemon.objects.filter(id=pokemon1_query).first()
            else:
                context['pokemon1'] = Pokemon.objects.filter(name__icontains=pokemon1_query).first()
        else:
            context['pokemon1'] = None
        
        
        if pokemon2_query:
            if pokemon2_query.isdigit():
                context['pokemon2'] = Pokemon.objects.filter(id=pokemon2_query).first()
            else:
                context['pokemon2'] = Pokemon.objects.filter(name__icontains=pokemon2_query).first()
        else:
            context['pokemon2'] = None
            
        context['default_image_url'] = default_image_url
        return context   

class PokemonBattleView(ListView):
    model = Pokemon
    template_name = 'pokedex/battle.html'
    context_object_name = 'all_pokemons'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pokemon1_query = self.request.GET.get('pokemon1')
        pokemon2_query = self.request.GET.get('pokemon2')
        move1_query = self.request.GET.get('move1')
        move2_query = self.request.GET.get('move2')

        default_image_url = '/static/pokedex/images/default.jpg'
        
        if pokemon1_query:
            if pokemon1_query.isdigit():
                context['pokemon1'] = Pokemon.objects.filter(id=pokemon1_query).first()
            else:
                context['pokemon1'] = Pokemon.objects.filter(name__icontains=pokemon1_query).first()
        else:
            context['pokemon1'] = None
        
        
        if pokemon2_query:
            if pokemon2_query.isdigit():
                context['pokemon2'] = Pokemon.objects.filter(id=pokemon2_query).first()
            else:
                context['pokemon2'] = Pokemon.objects.filter(name__icontains=pokemon2_query).first()
        else:
            context['pokemon2'] = None

        context['move1'] = Move.objects.filter(name__icontains=move1_query).first() if move1_query else None
        context['move2'] = Move.objects.filter(name__icontains=move2_query).first() if move2_query else None
        
        context['moves1'] = context['pokemon1'].moves.all() if context['pokemon1'] else None
        context['moves2'] = context['pokemon2'].moves.all() if context['pokemon2'] else None
        
        if context['pokemon1'] and context['pokemon2'] and context['move1'] and context['move2']:
            context['damage_to_pokemon2'] = self.calculate_damage(context['pokemon1'], context['pokemon2'], context['move1'])
            context['damage_to_pokemon1'] = self.calculate_damage(context['pokemon2'], context['pokemon1'], context['move2'])
        else:
            context['damage_to_pokemon2'] = None
            context['damage_to_pokemon1'] = None

        context['default_image_url'] = default_image_url
        return context
    
    def calculate_damage(self, attacker, defender, move):
        if not move or not move.type:
            return 0
        
        base_damage = move.power or 50
        attack_stat = attacker.attack
        defense_stat = defender.defense
        
        type_multiplier = 1.0
        move_type = move.type
        
        damage_multiplier = move_type.damage_multipliers()
        
        if defender.primary_type:
            type_multiplier *= damage_multiplier.get(defender.primary_type.name, 1.0)
        if defender.secondary_type:
            type_multiplier *= damage_multiplier.get(defender.secondary_type.name, 1.0)
        
        # Fórmula de dano
        damage = ( base_damage * (attack_stat / defense_stat) / 50 + 2) * type_multiplier
        
        return max(1, int(damage))

class TypeListView(ListAPIView):
    serializer_class = TypeSerializer

    def get_queryset(self):
        return Type.objects.all()


from django.shortcuts import render

def landing_page(request):
    return render(request, 'pokedex/landing.html')
    
