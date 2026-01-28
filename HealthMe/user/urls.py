from django.urls import path
from .views import home,registeration_view, login_view, logout_view
from . import views
urlpatterns = [
    path('', home, name='home'),
    path('register/', registeration_view, name='register'),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout" ),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.all_appointments, name='view_appointments'),
    path('appointments/edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('vulnerable-sql-test/', views.vulnerable_sql_test, name='vulnerable_sql_test'),



]
