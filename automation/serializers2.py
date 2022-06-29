from django.contrib.auth.models import User, Group
from rest_framework import serializers


class PlantSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    created = serializers.DateTimeField()
    title = serializers.CharField(max_length=100)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    rows = serializers.IntegerField()
    columns = serializers.IntegerField()


class MeasurementSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    name =serializers.CharField(max_length=100)
    row = serializers.IntegerField()
    col = serializers.IntegerField()
    meas_type = serializers.IntegerField(default=1)
    background_color = serializers.CharField(max_length=10, default="aqua")
    text_color = serializers.CharField(max_length=10, default="black")
    unit = serializers.CharField(max_length=10, default="m³/h")
    plant = serializers.PrimaryKeyRelatedField(read_only=True)
    auto_type = serializers.ReadOnlyField(default=10)


def material_default():
    return [0, 0, 0]

def connections_default():
    return [0, 0, 0, 0]

def connected_default():
    return [0, 0, 0, 0]

class AutomationSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    name =serializers.CharField(max_length=100)
    row = serializers.IntegerField()
    col = serializers.IntegerField()
    temperature = serializers.FloatField(default=21)
    material = serializers.JSONField(default=material_default)
    connections = serializers.JSONField(default=connections_default)
    connected = serializers.JSONField(default=connected_default)
    plant = serializers.PrimaryKeyRelatedField(read_only=True)
    auto_type = serializers.ReadOnlyField(default=0)


class ValveSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    open = serializers.BooleanField(default=False)  # valve initial state
    auto_type = serializers.ReadOnlyField(default=1)


class TankSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    height = serializers.FloatField(default=10.0) # tank height in meters
    volume = serializers.FloatField(default=10.0) # tank volume in meters ^ 3
    fill = serializers.FloatField(default=0.0) # beginning level in percent %
    fill_m3 = serializers.FloatField(default=0.0)  # beginning level in percent %
    auto_type = serializers.ReadOnlyField(default=2)


class ReactorSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    height = serializers.FloatField(default=10.0)  # tank height in meters
    volume = serializers.FloatField(default=10.0)  # tank volume in meters ^ 3
    fill = serializers.FloatField(default=0.0)  # beginning level in percent %
    fill_m3 = serializers.FloatField(default=0.0)  # beginning level in percent %
    auto_type = serializers.ReadOnlyField(default=8)
    set_temperature = serializers.FloatField(default=21.0) # set temperature in Ć
    set_pressure = serializers.FloatField(default=1.0) # set pressure in bars
    temperature_control = serializers.BooleanField(default=False) # temperature control on/off
    pressure_control = serializers.BooleanField(default=False) # pressure control on/off
    mixing_on = serializers.BooleanField(default=False)  # mixer on/off


class SourceSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    pressure = serializers.FloatField(default=10.0)  # tank height in meters
    auto_type = serializers.ReadOnlyField(default=5)


class TargetSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    auto_type = serializers.ReadOnlyField(default=6)


class PipeSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    dim = serializers.FloatField()
    auto_type = serializers.ReadOnlyField(default=3)


class PumpSerializer2(AutomationSerializer2):
    id = serializers.IntegerField()
    on = serializers.BooleanField(default=False)  # pump initial state
    end = serializers.IntegerField(default=1)  # pump direction 0 - 3 (Up, Right, Down, Left)
    speed = serializers.FloatField(default=0.0)  # pump initial speed in %
    auto_type = serializers.ReadOnlyField(default=4)


