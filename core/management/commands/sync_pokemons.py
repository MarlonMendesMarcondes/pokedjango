import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Pokemon, Move, Type, Ability

POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon/"

GENERATION_MAP = {
    "generation-i": 1,
    "generation-ii": 2,
    "generation-iii": 3,
    "generation-iv": 4,
    "generation-v": 5,
    "generation-vi": 6,
    "generation-vii": 7,
    "generation-viii": 8,
}

TYPE_COLORS = {
    "normal": "#A8A878",
    "fire": "#F08030",
    "water": "#6890F0",
    "electric": "#F8D030",
    "grass": "#78C850",
    "ice": "#98D8D8",
    "fighting": "#C03028",
    "poison": "#A040A0",
    "ground": "#E0C068",
    "flying": "#A890F0",
    "psychic": "#F85888",
    "bug": "#A8B820",
    "rock": "#B8A038",
    "ghost": "#705898",
    "dragon": "#7038F8",
    "dark": "#705848",
    "steel": "#B8B8D0",
    "fairy": "#EE99AC",
}



class Command(BaseCommand):
    help = "Sincroniza pokémons da PokéAPI para o banco local"

    def handle(self, *args, **options):
        self.sync_types()
        self.sync_pokemons()
            
    def sync_types(self):
        """Sincroniza os tipos de Pokémon com as cores do CSS."""
        self.stdout.write("Sincronizando tipos...")

        # Passo 1: Criar todos os tipos
        response = requests.get("https://pokeapi.co/api/v2/type")
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Erro ao buscar tipos da API"))
            return

        types_data = response.json()["results"]
        for type_data in types_data:
            type_name = type_data["name"]
            Type.objects.update_or_create(
                name=type_name,
                defaults={"color": TYPE_COLORS.get(type_name, "#FFFFFF")},
            )

        # Passo 2: Configurar as relações de efetividade
        for type_data in types_data:
            type_name = type_data["name"]
            type_url = type_data["url"]

            # Obtém os detalhes do tipo
            type_response = requests.get(type_url)
            if type_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Erro ao buscar detalhes do tipo {type_name}"))
                continue

            type_details = type_response.json()
            type_obj = Type.objects.get(name=type_name)

            # Limpa as relações existentes
            type_obj.strong_against.clear()
            type_obj.weak_against.clear()
            type_obj.no_effect_against.clear()

            # Configura as relações de efetividade
            for strong in type_details["damage_relations"]["double_damage_to"]:
                strong_type = Type.objects.filter(name=strong["name"]).first()
                if strong_type:
                    type_obj.strong_against.add(strong_type)

            for weak in type_details["damage_relations"]["double_damage_from"]:
                weak_type = Type.objects.filter(name=weak["name"]).first()
                if weak_type:
                    type_obj.weak_against.add(weak_type)

            for no_effect in type_details["damage_relations"]["no_damage_to"]:
                no_effect_type = Type.objects.filter(name=no_effect["name"]).first()
                if no_effect_type:
                    type_obj.no_effect_against.add(no_effect_type)

        self.stdout.write(self.style.SUCCESS("Tipos sincronizados com sucesso!"))

    def sync_abilities(self, pokemon, abilities_data):
        """Sincroniza as habilidades de um Pokémon."""
        pokemon.abilities.clear()  # Limpa as habilidades existentes

        for ability_entry in abilities_data:
            ability_name = ability_entry["ability"]["name"]
            ability_url = ability_entry["ability"]["url"]

            # Faz a requisição para obter detalhes da habilidade
            ability_response = requests.get(ability_url)
            if ability_response.status_code != 200:
                print(f"Erro ao buscar habilidade {ability_name}")
                continue

            ability_json = ability_response.json()
            description = None

            # Obtém a descrição da habilidade em inglês
            for entry in ability_json.get("effect_entries", []):
                if entry["language"]["name"] == "en":
                    description = entry.get("effect")
                    break

            # Cria ou atualiza a habilidade no banco de dados
            ability, _ = Ability.objects.update_or_create(
                name=ability_name,
                defaults={"description": description},
            )

            # Adiciona a habilidade ao Pokémon
            pokemon.abilities.add(ability)
    
    def sync_pokemons(self):
        """Sincroniza os Pokémon da PokéAPI."""
        for i in range(1, 1026):  # Pokémons de 1 a 251
            url = f"{POKEAPI_BASE}{i}/"
            response = requests.get(url)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Erro ao buscar Pokémon {i}"))
                continue

            data = response.json()
            self.sync_pokemon(data)

    def sync_pokemon(self, data):
        """Sincroniza um único Pokémon."""
        name = data["name"]
        image_url = data["sprites"]["other"]["dream_world"]["front_default"]
        stats = {item["stat"]["name"]: item["base_stat"] for item in data.get("stats", [])}

        # Obtém os tipos
        primary_type_name = data['types'][0]['type']['name']
        secondary_type_name = data['types'][1]['type']['name'] if len(data['types']) > 1 else None

        primary_type = Type.objects.get(name=primary_type_name)
        secondary_type = Type.objects.get(name=secondary_type_name) if secondary_type_name else None

        # Obtém a geração
        generation, generation_number = self.get_generation(data)

        # Cria ou atualiza o Pokémon
        pokemon, created = Pokemon.objects.update_or_create(
            name=name,
            defaults={
                "base_experience": data["base_experience"],
                "height": data["height"],
                "weight": data["weight"],
                "image_url": image_url,
                "hp": stats.get("hp"),
                "attack": stats.get("attack"),
                "defense": stats.get("defense"),
                "special_attack": stats.get("special-attack"),
                "special_defense": stats.get("special-defense"),
                "speed": stats.get("speed"),
                "primary_type": primary_type,
                "secondary_type": secondary_type,
                "generation": generation,
                "generation_number": generation_number,
            },
        )
        # Baixa a imagem do Pokémon
        if image_url and not pokemon.image:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Atualiza a imagem, mesmo que já exista
                pokemon.image.save(f"{name}.svg", ContentFile(image_response.content))
            else:
                self.stdout.write(self.style.ERROR(f"Erro ao baixar imagem de {name}"))
        
        # Sincroniza os movimentos
        self.sync_moves(pokemon, data["moves"])

        # Sincroniza as habilidades
        self.sync_abilities(pokemon, data["abilities"])

        self.stdout.write(self.style.SUCCESS(
            f"{'Criado' if created else 'Atualizado'}: {name} "
            f"(HP: {pokemon.hp}, "
            f"ATK: {pokemon.attack}, "
            f"DEF: {pokemon.defense}, "
            f"SP.ATK: {pokemon.special_attack}, "
            f"SP.DEF: {pokemon.special_defense}, "
            f"SPD: {pokemon.speed}) "
            f"Tipos: {pokemon.primary_type.name}"
            + (f"/{pokemon.secondary_type.name}" if pokemon.secondary_type else "")
            + f" - {pokemon.moves.count()} movimentos"
        ))

    def get_generation(self, data):
        """Obtém a geração do Pokémon."""
        species_url = data["species"]["url"]
        species_response = requests.get(species_url)

        if species_response.status_code == 200:
            species_data = species_response.json()
            generation = species_data["generation"]["name"]
            generation_number = GENERATION_MAP.get(generation, None)
            return generation, generation_number

        return None, None

    def sync_moves(self, pokemon, moves_data):
        """Sincroniza os movimentos de um Pokémon."""
        pokemon.moves.clear()

        for move_entry in moves_data[:20]:  # Limita a 10 movimentos
            move_data = move_entry["move"]
            move_url = move_data["url"]

            move_response = requests.get(move_url)
            if move_response.status_code != 200:
                continue

            move_json = move_response.json()
            move_name = move_json["name"]
            power = move_json.get("power")
            accuracy = move_json.get("accuracy")
            type_name = move_json["type"]["name"]
            
            # Busca a instância do tipo correspondente
            move_type = Type.objects.filter(name=type_name).first()
            if not move_type:
                self.stdout.write(self.style.WARNING(f"Tipo '{type_name}' não encontrado para o movimento '{move_name}'"))
                continue

            effect_entries = move_json.get("effect_entries", [])
            effect = None
            for entry in effect_entries:
                if entry["language"]["name"] == "en":
                    effect = entry.get("effect")
                    break

            move, _ = Move.objects.update_or_create(
                name=move_name,
                defaults={
                    "power": power,
                    "accuracy": accuracy,
                    "type": move_type,
                    "effect": effect,
                },
            )

            pokemon.moves.add(move)        