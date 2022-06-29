"""processdemodata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from automation import views

router = routers.DefaultRouter()
router.register(r'plants', views.PlantViewSet)
router.register(r'pipes', views.PipeViewSet)
router.register(r'tanks', views.TankViewSet)
router.register(r'valves', views.ValveViewSet)
router.register(r'pumps', views.PumpViewSet)
router.register(r'sources', views.SourceViewSet)
router.register(r'targets', views.TargetViewSet)
router.register(r'reactors', views.ReactorViewSet)
router.register(r'pids', views.PIDViewSet)
router.register(r'measurements', views.MeasurementViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'phases', views.PhaseViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'usersbyname', views.UserByNameViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('autoregister/', views.AutomationRegisterView.as_view()),
    path('plantdata/<int:plant>/', views.PlantData.as_view()),
    path('plantcopy/<int:plant>/', views.PlantCopy.as_view()),
    path('recipedata/<int:recipe>/', views.RecipeData.as_view()),
    path('recipecopy/<int:recipe>/', views.RecipeCopy.as_view()),
]
