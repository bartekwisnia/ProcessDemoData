from django.contrib.auth.models import User, Group
from .models import Plant, Pipe, Tank, Valve, Pump, Automation, Measurement, PID, Recipe, Phase, Source, Target, Reactor
from rest_framework import serializers


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'


class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = '__all__'


class PipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipe
        fields = '__all__'


class TankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tank
        fields = '__all__'


class ReactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reactor
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = '__all__'


class ValveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valve
        fields = '__all__'

class PumpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pump
        fields = '__all__'


class PIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = PID
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'url', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']