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
router.register(r'hospital_doctor_timeslots', HospitalDoctorTimeSlotGroupViewSet, basename='hospital_doctor_timeslot')
hospital_doctor_profile_update = HospitalDoctorProfileViewSet.as_view({
    'patch': 'partial_update'
})

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
    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),


    path("predict/", depression_predict, name="depression_predict"),
    path("predict-adhd/", views.adhd_predict, name="adhd_predict"),
    path("user_view_book/", UserViewBook.as_view(), name="user_view_book"),
    path('view_hospital_doctor/<int:doctor_id>/', views.view_hospital_doctor_profile, name='view_hospital_doctor_profile'),
    path('hospital_doctor/update/<int:pk>/', hospital_doctor_profile_update, name='hospital_doctor_profile_update'),
    path('hospital-doctor/<int:doctor_id>/availability/', views.update_hospital_doctor_availability, name='update_hospital_doctor_availability'),
    path('hospital/doctor/<int:doctor_id>/timeslots/', view_hospital_doctor_timeslots, name='view_hospital_doctor_timeslots'),
    path('view_nearby_hospital_doctors/<int:user_id>/', views.view_nearby_hospital_doctors, name='view_nearby_hospital_doctors'),
    path('user-hospital/doctor/feedback/add/', views.add_hospital_doctor_feedback, name='add_hospital_doctor_feedback'),
    path('hospital/doctor/<int:doctor_id>/feedback/', views.view_hospital_doctor_feedback, name='view_hospital_doctor_feedback'),
    path('doctor/<int:doctor_id>/feedback/', GetDoctorFeedbackAPI.as_view(), name='doctor_feedback'),
    path('hospital/doctor/book-slot/', views.book_hospital_doctor_slot, name='book_hospital_doctor_slot'),
    path('user/<int:user_id>/hospital/bookings/', views.user_view_booking_hospital.as_view(), name='user_view_hospital_bookings'),
    path('hospital/doctor/<int:doctor_id>/bookings/', views.doctor_view_booking_hospital.as_view(), name='doctor_view_booking_hospital'),
]