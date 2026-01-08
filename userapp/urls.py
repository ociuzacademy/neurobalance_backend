# urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .import views
# import your viewsets
from userapp.views import *

# router setup
router = routers.DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'hospital_doctors', HospitalDoctorRegisterViewSet,basename='doctor_register')

# Swagger setup
schema_view = get_schema_view(
    openapi.Info(
        title="Neurobalance API",
        default_version='v1',
        description="API documentation with Swagger & DRF Router",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path("predict/", depression_predict, name="depression_predict"),
    path("predict-adhd/", views.adhd_predict, name="adhd_predict"),
    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),


   
]