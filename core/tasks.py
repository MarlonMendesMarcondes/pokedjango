from celery import shared_task
from core.management.commands.sync_pokemons import Command as SyncCommand
import requests
from core.models import Pokemon
from django.db import connection

@shared_task
def sync_pokemon_task(pokemon_id):
    """Sincroniza um único Pokémon pelo ID."""
    pokemon = Pokemon.objects.get(id=pokemon_id)
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon.name.lower()}/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        sync_command = SyncCommand()
        sync_command.sync_pokemon(data)
        connection.close()
        return f"Pokémon {pokemon.name} atualizado com sucesso!"
    
    return f"Erro ao atualizar o Pokémon {pokemon.name}."