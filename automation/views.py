from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from dj_rest_auth.registration.views import RegisterView
from .models import Plant, Pipe, Tank, Valve, Pump, Automation, Measurement, PID, Recipe, Phase, Source, Target, Reactor
from .serializers import UserSerializer, GroupSerializer, PlantSerializer, PipeSerializer, TankSerializer, \
    ValveSerializer, PumpSerializer, AutomationSerializer, MeasurementSerializer, PIDSerializer, RecipeSerializer, \
    PhaseSerializer, SourceSerializer, TargetSerializer, ReactorSerializer


class PlantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Plant.objects.all().order_by('-created')
    serializer_class = PlantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Plant.objects.all() if user.is_superuser else Plant.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['owner'] = request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        print(request)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlantCopy(APIView):
    """
    View to copy an existing array
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, plant, format=None):
        """
        Copy existing plant
        """
        plant_ob = Plant.objects.get(pk=plant)
        plant_ob = plant_ob.copy()
        return Response(data=PlantSerializer(plant_ob).data, status=status.HTTP_200_OK)


class PlantData(APIView):
    """
    View to an array of plant elements
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, plant, format=None):
        """
        Return a list of all users.
        """
        user = self.request.user

        plant_ob = Plant.objects.get(pk=plant)
        if plant_ob.owner != user and not user.is_superuser:
            return Response(data={}, status=status.HTTP_401_UNAUTHORIZED)

        arr_ao = [[0 for i in range(plant_ob.columns)] for j in range(plant_ob.rows)]
        arr_m = [[list() for i in range(plant_ob.columns)] for j in range(plant_ob.rows)]
        arr_pid = []

        pipes = plant_ob.pipes.all()
        tanks = plant_ob.tanks.all()
        pumps = plant_ob.pumps.all()
        valves = plant_ob.valves.all()
        sources = plant_ob.sources.all()
        targets = plant_ob.targets.all()
        reactors = plant_ob.reactors.all()
        measurements = list(plant_ob.measurements.all())
        pids = list(plant_ob.pids.all())

        auto_objects = list(pipes) + list(tanks) + list(pumps) + list(valves) + list(sources) + list(targets) \
                       + list(reactors)
        for ao in auto_objects:
            try:
                arr_ao[ao.row][ao.col] = ao.serialize()
            except IndexError:
                ...
                print("Index: {0}:{1} is out of plant size".format(ao.row, ao.col))

        for m in measurements:
            try:
                arr_m[m.row][m.col].append(m.serialize())
            except IndexError:
                ...
                print("Index: {0}:{1} is out of plant size".format(m.row, m.col))

        for pid in pids:
            pid_data = PIDSerializer(pid).data
            pid_data['actuator'] = {"row": pid.actuator.row, "col": pid.actuator.col}
            pid_data['measurement'] = {"row": pid.measurement.row, "col": pid.measurement.col, "meas_type": pid.measurement.meas_type}
            arr_pid.append(pid_data)

        return Response({"automation": arr_ao, "measurements": arr_m, "pids": arr_pid})


    def put(self, request, plant, format=None):
        user = self.request.user
        created = 0
        plant_ob = Plant.objects.get(pk=plant)
        if plant_ob.owner != user and not user.is_superuser:
            return Response(data={}, status=status.HTTP_401_UNAUTHORIZED)

        existing_ao = [0,0,0,0,0,0,0,0,0]
        existing_ao[1] = plant_ob.valves.all()
        existing_ao[2] = plant_ob.tanks.all()
        existing_ao[3] = plant_ob.pipes.all()
        existing_ao[4] = plant_ob.pumps.all()
        existing_ao[5] = plant_ob.sources.all()
        existing_ao[6] = plant_ob.targets.all()
        existing_ao[8] = plant_ob.reactors.all()
        existing_m =plant_ob.measurements.all()
        existing_pid = plant_ob.pids.all()

        row = 0
        serializers = [AutomationSerializer, ValveSerializer, TankSerializer, PipeSerializer, PumpSerializer,
                       SourceSerializer, TargetSerializer, None, ReactorSerializer]
        models = [Automation, Valve, Tank, Pipe, Pump, Source, Target, None, Reactor]
        request_auto = request.data['automation']
        request_meas = request.data['measurements']
        request_pids = request.data['pids']
        new_ao = []
        for rows in request_auto:
            col = 0
            for ao in rows:
                ao.update({"plant": plant, "row": row, "col": col})
                col += 1
                if ao['auto_type'] in [1,2,3,4,5,6,8]:
                    try:
                        existing_ob = existing_ao[ao['auto_type']].get(id=ao['id'])
                    except models[ao['auto_type']].DoesNotExist:
                        existing_ob = None
                    serializer = serializers[ao['auto_type']](existing_ob, data=ao)

                    if serializer.is_valid():
                        new_ob = serializer.save()
                        if ao['id'] != new_ob.id:
                            created += 1
                            new_ao.append(new_ob)
                        existing_ao[ao['auto_type']] = existing_ao[ao['auto_type']].exclude(id=new_ob.id)
                    else:
                        print(serializer.data)
                        # do_not_delete_ao[ao['auto_type']].append(new_ob.id)
                        existing_ao[ao['auto_type']] = existing_ao[ao['auto_type']].exclude(id=existing_ob.id)
            row+=1

        row = 0
        new_meas =[]
        for rows in request_meas:
            col = 0
            for meas_list in rows:
                for m in meas_list:
                    try:
                        existing_m_ob = existing_m.get(id=m['id'])
                    except Measurement.DoesNotExist:
                        existing_m_ob = None
                    m.update({"plant": plant, "row": row, "col": col})
                    serializer = MeasurementSerializer(existing_m_ob, data=m)
                    if serializer.is_valid():
                        new_ob = serializer.save()
                        if m['id'] != new_ob.id:
                            new_meas.append(new_ob)
                            created += 1
                        existing_m = existing_m.exclude(id=new_ob.id)
                    else:
                        print(serializer.data)
                        existing_m = existing_m.exclude(id=existing_m_ob.id)

                col += 1
            row+=1
        for pid in request_pids:
            try:
                existing_pid_ob = existing_pid.get(id=pid['id'])
            except PID.DoesNotExist:
                existing_pid_ob = None
            pid.update({"plant": plant})
            if (pid['meas']):
                if(pid['meas']['id'] > 0):
                    pid.update({"measurement": pid['meas']['id']})
                else:
                    meas_id = next(m.id for m in new_meas if m.row == pid['meas']['row'] and m.col==pid['meas']['col'] and m.meas_type==pid['meas']['meas_type'])
                    pid.update({"measurement": meas_id})
            if (pid['act']):
                if (pid['act']['id'] > 0):
                    pid.update({"actuator": pid['act']['id']})
                else:
                    act_id = next(act for act in new_ao if act["row"] == pid['act']['row'] and act["col"] == pid['act']['col'])
                    pid.update({"actuator": act_id})

            serializer = PIDSerializer(existing_pid_ob, data=pid)
            if serializer.is_valid():
                new_ob = serializer.save()
                if pid['id'] != new_ob.id:
                    created += 1
                existing_pid = existing_pid.exclude(id=new_ob.id)
            else:
                print(serializer.data)
                existing_pid = existing_pid.exclude(id=existing_pid_ob.id)

        print("created: {}".format(created))

        idx = 0
        for ao_qs in existing_ao:
            if ao_qs != 0:
                ao_qs.all().delete()
            idx += 1
        existing_m.all().delete()
        existing_pid.all().delete()

        return Response(data=request.data, status=status.HTTP_200_OK)


class MeasurementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Measurement.objects.all().order_by('plant')
    serializer_class = MeasurementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Measurement.objects.all() if user.is_superuser else Measurement.objects.filter(plant__owner=user)


class PipeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Pipe.objects.all().order_by('plant')
    serializer_class = PipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Pipe.objects.all() if user.is_superuser else Pipe.objects.filter(plant__owner=user)
    

class TankViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tank.objects.all().order_by('plant')
    serializer_class = TankSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Tank.objects.all() if user.is_superuser else Tank.objects.filter(plant__owner=user)


class ReactorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Reactor.objects.all().order_by('plant')
    serializer_class = ReactorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Reactor.objects.all() if user.is_superuser else Reactor.objects.filter(plant__owner=user)


class SourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Source.objects.all().order_by('plant')
    serializer_class = SourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Source.objects.all() if user.is_superuser else Source.objects.filter(plant__owner=user)


class TargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Target.objects.all().order_by('plant')
    serializer_class = TargetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Target.objects.all() if user.is_superuser else Target.objects.filter(plant__owner=user)
        
        
class PumpViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Pump.objects.all().order_by('plant')
    serializer_class = PumpSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Pump.objects.all() if user.is_superuser else Pump.objects.filter(plant__owner=user)


class ValveViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Valve.objects.all().order_by('plant')
    serializer_class = ValveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Valve.objects.all() if user.is_superuser else Valve.objects.filter(plant__owner=user)


class PIDViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PID.objects.all().order_by('plant')
    serializer_class = PIDSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PID.objects.all() if user.is_superuser else PID.objects.filter(plant__owner=user)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Recipe.objects.all().order_by('plant')
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all() if user.is_superuser else Recipe.objects.filter(plant__owner=user)
        if 'plant' in self.request.query_params:
            queryset = queryset.filter(plant=self.request.query_params['plant'])
 
        return queryset

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        kwargs['partial'] = True
        phases = request.data.pop('phases', [])
        index = 0
        created = 0
        deleted = 0
        updated = 0
        existing_phases = Phase.objects.filter(recipe=recipe)
        for p in phases:
            p.update({"recipe": recipe.id, "index": index})
            print(p)
            index += 1
            try:
                existing_phase = existing_phases.get(id=p['id'])
            except Phase.DoesNotExist:
                existing_phase = None
            serializer = PhaseSerializer(existing_phase, data=p)
            if serializer.is_valid():
                p_obj = serializer.save()
                if p['id'] != p_obj.id:
                    created += 1
                else:
                    updated += 1
                existing_phases = existing_phases.exclude(id=p_obj.id)
            elif existing_phase:
                existing_phases = existing_phases.exclude(id=existing_phase.id)
        deleted = existing_phases.all().count()
        existing_phases.all().delete()
        print("created:{}, updated:{}, deleted:{}".format(created, updated, deleted))
        return super().update(request, *args, **kwargs)
    
    
class RecipeData(APIView):
    """
    View to an array of plant elements
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, recipe, format=None):
        """
        Return a list of all users.
        """
        user = self.request.user

        if not recipe:
            return Response(data={}, status=status.HTTP_400_BAD_REQUEST)

        recipe_ob = Recipe.objects.get(pk=recipe)
        if recipe_ob.plant.owner != user and not user.is_superuser:
            return Response(data={}, status=status.HTTP_401_UNAUTHORIZED)

        phases = list(recipe_ob.phases.all())
        phases_serialized = [PhaseSerializer(phase).data for phase in phases]
        print(phases_serialized)
        return Response(phases_serialized)


class RecipeCopy(APIView):
    """
    View to copy an existing recipe
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, recipe, format=None):
        """
        Copy existing plant
        """
        recipe_ob = Recipe.objects.get(pk=recipe)
        recipe_ob = recipe_ob.copy()
        return Response(data=RecipeSerializer(recipe_ob).data, status=status.HTTP_200_OK)


class PhaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Phase.objects.all().order_by('recipe')
    serializer_class = PhaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Phase.objects.all() if user.is_superuser else Phase.objects.filter(plant__owner=user)
        if 'recipe' in self.request.query_params:
            queryset.filter(plant=self.request.query_params['recipe'])

        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserByNameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class AutomationRegisterView(RegisterView):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        demo_user = get_user_model().objects.get(username="demo")
        demo_plants = Plant.objects.filter(owner=demo_user)
        print(demo_plants)
        for dp in demo_plants:
            dp = dp.copy(user)
            dp.owner=user
            dp.save()

        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response