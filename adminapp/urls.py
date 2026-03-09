from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('login/', admin_login, name='admin_login'),
    path('', admin_dashboard, name='admin_dashboard'),
    path('logout/', admin_logout, name='admin_logout'),
    path('view_users/', views.view_users, name='view_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('view_pending_doctors/', views.view_pending_doctors, name='view_pending_doctors'),
    path('view-all-bookings/', views.admin_view_hospital_bookings, name='view_all_bookings'),
    # Hospital Doctor Actions
    path('approve_hospital_doctor/<int:doctor_id>/', views.approve_hospital_doctor, name='approve_hospital_doctor'),
    path('reject_hospital_doctor/<int:doctor_id>/', views.reject_hospital_doctor, name='reject_hospital_doctor'),
    path('view_approved_doctors/', views.view_approved_doctors, name='view_approved_doctors'),
    path('view_rejected_doctors/', views.view_rejected_doctors, name='view_rejected_doctors'),
    path("add-book/", views.add_book, name="add_book"),
    path("books/", views.view_books, name="view_books"),
    path("edit-book/<int:pk>/", views.edit_book, name="edit_book"),
    path("delete-book/<int:pk>/", views.delete_book, name="delete_book"),

]