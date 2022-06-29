from django.db import models
from django.contrib.auth import get_user_model
from .serializers2 import PipeSerializer2, TankSerializer2, ValveSerializer2, PumpSerializer2, MeasurementSerializer2, \
    SourceSerializer2, TargetSerializer2, ReactorSerializer2, material_default, connections_default, connected_default



class Plant(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,)
    rows = models.IntegerField(default=5)
    columns = models.IntegerField(default=5)

    class Meta:
        ordering = ['owner']

    def copy(self, new_owner=None):
        """
        Copy existing plant
        """

        # get plant children
        pipes = self.pipes.all()
        tanks = self.tanks.all()
        pumps = self.pumps.all()
        valves = self.valves.all()
        sources = self.sources.all()
        targets = self.targets.all()
        reactors = self.reactors.all()
        measurements = self.measurements.all()
        pids = self.pids.all()
        recipes = self.recipes.all()

        auto_objects = list(pipes) + list(tanks) + list(pumps) + list(valves) + list(sources) + list(targets) \
                       + list(reactors) + list(measurements) + list(pids)
        list_recipes = list(recipes)

        # copy plant
        if not new_owner:
            self.title += "_copy"
        self.pk = None
        self._state.adding = True
        self.save()

        storage = []
        for ao in auto_objects:
            old_id = ao.id
            ao.pk = None
            ao.id = None
            ao._state.adding = True
            ao.plant = self
            ao.save()
            storage.append({"new_object": ao, "old_id": old_id})

        for pid in pids:
            try:
                pid.measurement = next(strg["new_object"] for strg in storage if strg["old_id"] == pid.measurement.id and
                                       strg["new_object"].__class__.__name__ == pid.measurement.__class__.__name__)
            except StopIteration:
                pid.measurement = None
            try:
                pid.actuator = next(strg["new_object"] for strg in storage if strg["old_id"] == pid.actuator.id and
                                    strg["new_object"].__class__.__name__ == pid.actuator.__class__.__name__)
            except StopIteration:
                pid.actuator = None
            pid.save()

        for rec in list_recipes:
            rec = rec.copy(self)
            rec.plant = self
            rec.save()

        return self


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    plant = models.ForeignKey(Plant, related_name='recipes', on_delete=models.CASCADE)
    step = models.IntegerField(default=0)
    state = models.IntegerField(default=0)

    class Meta:
        ordering = ['plant']

    def copy(self, new_plant=None):
        """
        Copy existing recipe
        """

        # get recipe phases
        phases = self.phases.all()
        list_phases = list(phases)

        # copy recipe
        if not new_plant:
            self.title += "_copy"
        self.pk = None
        self._state.adding = True
        self.save()

        # copy phaes
        for ph in list_phases:
            ph.pk = None
            ph.id = None
            ph._state.adding = True
            ph.recipe = self
            ph.save()

        return self


class Phase(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='phases', on_delete=models.CASCADE)
    phase_num = models.IntegerField()
    index = models.IntegerField()
    parameters = models.JSONField()
    end_cond = models.IntegerField(default=0)
    in_background = models.BooleanField(default=False)

    class Meta:
        ordering = ['recipe']


class Measurement(models.Model):
    name = models.CharField(max_length=100, blank=True)
    plant = models.ForeignKey(Plant, related_name='measurements', on_delete=models.CASCADE)
    row = models.IntegerField()
    col = models.IntegerField()
    meas_type = models.IntegerField(default=1)
    background_color = models.CharField(max_length=10, default="aqua")
    text_color = models.CharField(max_length=10, default="black")
    unit = models.CharField(max_length=10, default="m³/h")

    def serialize(self):
        return MeasurementSerializer2(self).data

    class Meta:
        ordering = ['row','col']


class Automation(models.Model):
    name = models.CharField(max_length=100, blank=True)

    row = models.IntegerField()
    col = models.IntegerField()
    temperature = models.FloatField(default=21.0)  # temperature of medium
    material = models.JSONField(default=material_default)
    connections = models.JSONField(default=connections_default)
    connected = models.JSONField(default=connected_default)

    class Meta:
        ordering = ['row','col']


class Pipe(Automation):
    plant = models.ForeignKey(Plant, related_name='pipes', on_delete=models.CASCADE)
    dim = models.IntegerField(default=60) #pipe diameter in milimeters

    def serialize(self):
        return PipeSerializer2(self).data


class Tank(Automation):
    plant = models.ForeignKey(Plant, related_name='tanks', on_delete=models.CASCADE)
    height = models.FloatField(default=10.0) # tank height in meters
    volume = models.FloatField(default=10.0) # tank volume in meters ^ 3
    fill = models.FloatField(default=0.0) # beginning level in percent %
    fill_m3 = models.FloatField(default=0.0) # beginning level in percent m3

    def serialize(self):
        return TankSerializer2(self).data


class Reactor(Automation):
    plant = models.ForeignKey(Plant, related_name='reactors', on_delete=models.CASCADE)
    height = models.FloatField(default=10.0) # tank height in meters
    volume = models.FloatField(default=10.0) # tank volume in meters ^ 3
    fill = models.FloatField(default=0.0) # beginning level in percent %
    fill_m3 = models.FloatField(default=0.0) # beginning level in percent m3
    set_temperature = models.FloatField(default=21.0) # set temperature in Ć
    set_pressure = models.FloatField(default=1.0) # set pressure in bars
    temperature_control = models.BooleanField(default=False) # temperature control on/off
    pressure_control = models.BooleanField(default=False) # pressure control on/off
    mixing_on = models.BooleanField(default=False)  # mixer on/off

    def serialize(self):
        return ReactorSerializer2(self).data


class Source(Automation):
    plant = models.ForeignKey(Plant, related_name='sources', on_delete=models.CASCADE)
    pressure = models.FloatField(default=4.0) # source pressure in bars

    def serialize(self):
        return SourceSerializer2(self).data


class Target(Automation):
    plant = models.ForeignKey(Plant, related_name='targets', on_delete=models.CASCADE)

    def serialize(self):
        return TargetSerializer2(self).data


class Pump(Automation):
    plant = models.ForeignKey(Plant, related_name='pumps', on_delete=models.CASCADE)
    on = models.BooleanField(default=False) # pump initial state
    end = models.IntegerField(default=1) # pump direction 0 - 3 (Up, Right, Down, Left)
    speed = models.FloatField(default=0.0) # pump initial speed in %

    def serialize(self):
        return PumpSerializer2(self).data


class Valve(Automation):
    plant = models.ForeignKey(Plant, related_name='valves', on_delete=models.CASCADE)
    open = models.BooleanField(default=False) # valve initial state

    def serialize(self):
        return ValveSerializer2(self).data


class PID(models.Model):
    name = models.CharField(max_length=100, blank=True)
    plant = models.ForeignKey(Plant, related_name='pids', on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, related_name='pids', on_delete=models.SET_NULL, null=True)
    actuator = models.ForeignKey(Pump, related_name='pids', on_delete=models.SET_NULL, null=True)
    sp = models.FloatField(default=50.0) # setpoint
    mv = models.FloatField(default=0.0) # controllers output
    p_faktor = models.FloatField(default=0.0)  # controllers output
    i_faktor = models.FloatField(default=0.0)  # controllers output
    d_faktor = models.FloatField(default=0.0)  # controllers output
    on = models.BooleanField(default=False)  # Initial state
