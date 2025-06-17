from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.html import format_html
from core.models import Pokemon, Move, Type ,Ability
from core.tasks import sync_pokemon_task
from core.filters import HasImageFilter

class MoveInline(TabularInline):
    model = Pokemon.moves.through   # Relacionamento ManyToMany
    extra = 0

class PokemonAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'id','name', 'base_experience', 'height', 'weight', 'primary_type', 'secondary_type')
    search_fields = ('id','name', 'moves__name')
    list_filter = ('primary_type', 'secondary_type', HasImageFilter)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('image_admin','name', 'primary_type', 'secondary_type'),
            'classes': ('card',),
        }),
        ('Estatísticas', {
            'fields': ('base_experience', 'height', 'weight'),
            'classes': ('card',),
        }),
        ('Estatísticas de Batalha', {
            'fields': ('hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed'),
            'classes': ('card',),
        }),
        ('Outras Informações', {
            'fields': ('generation', 'generation_number'),
            'classes': ('card',),
        }),
        ('Imagem URL', {
            'fields': ('image_url',),
            'classes': ('card',),
        }),
    )
    readonly_fields = readonly_fields = ('image_admin', 'name', 'primary_type', 'secondary_type', 'base_experience', 'height', 'weight', 'image_tag')
    inlines= [MoveInline]
    actions = ['sync_selected_pokemons']  # Adiciona a action no admin

    def sync_selected_pokemons(self, request, queryset):
        """Envia os Pokémon selecionados para sincronização assíncrona."""
        for pokemon in queryset:
            sync_pokemon_task.delay(pokemon.id)  # Chama a tarefa Celery de forma assíncrona
        self.message_user(request, "A sincronização foi iniciada. Isso pode levar alguns minutos.")

    sync_selected_pokemons.short_description = "Atualizar Pokémon selecionados"

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url)
        return "Sem imagem"
    image_tag.short_description = "Imagem"
    
    def image_admin(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="{}" />', obj.image.url, obj.card_style)
        return "Sem imagem"
    image_tag.short_description = "Imagem"
    
    def type_colored_background(self, obj):
        # Acessa a cor do tipo primário
        if obj.primary_type.cor :
            return format_html(
                '<div style="background-color: {}; padding: 10px; border-radius: 5px; text-align: center;">{}</div>',
                obj.primary_type.cor,  # Usa o campo `cor` do modelo 
            )
        return "Sem cor definida"
    type_colored_background.short_description = "Cor do Tipo"
        
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Adiciona o CSS personalizado
        }
    
class MoveAdmin(admin.ModelAdmin):
    list_display = ('name', 'power', 'accuracy', 'type')
    search_fields = ('name',)
    list_filter = ('type',)
    
class TypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)
    list_filter = ('name',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'color'),
            'classes': ('card',),
        }),
    )
    readonly_fields = ('name', 'color')
    def color_tag(self, obj):
        return format_html('<div style="background-color: {}; width: 50px; height: 20px;"></div>', obj.color)
    color_tag.short_description = "Cor"
    
class AbilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description'),
            'classes': ('card',),
        }),
    )
    readonly_fields = ('name', 'description')
    

    
        
admin.site.register(Pokemon, PokemonAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Ability, AbilityAdmin)

