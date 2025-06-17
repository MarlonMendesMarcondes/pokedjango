from django.db import models

class Move(models.Model):
    name = models.CharField(max_length=100, unique=True)
    power = models.IntegerField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey('Type', on_delete=models.CASCADE, related_name='moves',null=True, blank=True)
    effect = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Type(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7)  # Hex color code
    strong_against = models.ManyToManyField('self', related_name='weak_to', symmetrical=False, blank=True)
    weak_against = models.ManyToManyField('self', related_name='strong_to', symmetrical=False, blank=True)
    no_effect_against = models.ManyToManyField('self', related_name='immune_to', symmetrical=False, blank=True)

    def __str__(self):
        return self.name
    
    def damage_multipliers(self):
        """
        Retorna os multiplicadores de dano para o tipo atual.
        """
        multipliers = {}
        all_types = Type.objects.all()

        for t in all_types:
            if t in self.strong_against.all():
                multipliers[t.name] = 2.0  # Dano dobrado
            elif t in self.weak_against.all():
                multipliers[t.name] = 0.5  # Dano reduzido pela metade
            elif t in self.no_effect_against.all():
                multipliers[t.name] = 0.0  # Sem efeito
            else:
                multipliers[t.name] = 1.0  # Dano normal

        return multipliers
    
class Ability(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Pokemon(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(blank=True, null=True)
    image = models.FileField(upload_to="pokemons/", blank=True, null=True)
    base_experience = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()
    
    primary_type = models.ForeignKey(
        Type, on_delete=models.SET_NULL, related_name="primary_pokemons", null=True
    )
    secondary_type = models.ForeignKey(
        Type, on_delete=models.SET_NULL, related_name="secondary_pokemons", null=True, blank=True
    )
    
    hp = models.IntegerField(null=True)
    attack = models.IntegerField(null=True)
    defense = models.IntegerField(null=True)
    special_attack = models.IntegerField(null=True)
    special_defense = models.IntegerField(null=True)
    speed = models.IntegerField(null=True)
    
    moves = models.ManyToManyField(Move, related_name="pokemons")
    abilities = models.ManyToManyField(Ability, related_name="pokemons")
    
    generation = models.CharField(null=True)
    generation_number = models.PositiveIntegerField(null=True)

    
    def total_stats(self):
        return self.hp + self.attack + self.defense + self.special_attack + self.special_defense + self.speed
    
    @property
    def card_style(self):
        """Gera o estilo de fundo do card com base nos tipos do Pokémon."""
        primary_color = self.primary_type.color if self.primary_type else "#E6E6E6"
        secondary_color = self.secondary_type.color if self.secondary_type else primary_color
        return f"background: linear-gradient(135deg, {primary_color}, {secondary_color}), url('../static/pokedex/img/texture.jpg'); width: 18rem"

    
    def __str__(self):
        return self.name