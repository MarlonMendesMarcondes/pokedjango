from rest_framework import serializers
from .models import Type

class TypeSerializer(serializers.ModelSerializer):
    damage_multipliers = serializers.SerializerMethodField()
    
    class Meta:
        model = Type
        fields = ['id', 'name', 'color', 'damage_multipliers']
        
    def get_damage_multipliers(self, instance):
        """
        Retorna os multiplicadores de dano para o tipo atual.
        """
        def get_damage_multipliers(self, obj):
            return obj.damage_multipliers()