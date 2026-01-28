from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from .models import Doctor, Appointment
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_staff or user.is_superuser

def is_patient(user):
    return hasattr(user, 'patient')

def home(request):
    return render(request, 'home.html')

def registeration_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST ['confirm_password']

        if password == confirm_password:
            try:
                user = User.objects.create_user(username = username, password= password)
                user.save()
                login(request, user)
                return redirect('home')
            except:
                messages.error(request, "Username already exists")
        else: 
             messages.error(request, "password do not match")
    return render(request, "registration/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect ('login')

def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashbaord.html')

def patient_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return render(request, 'patient_dashboard.html')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def is_admin(user):
    return user.is_staff

from django.contrib.auth.decorators import login_required
from .models import Appointment, Doctor

#patient dashbaord after login
@login_required
def patient_dashboard(request):
    doctors = Doctor.objects.all()
    #show appointment belong to the patient
    appointments = Appointment.objects.filter(patient=request.user)
    #return all the selective data by patient to patient_dashboard mcm doc, appt
    return render(request, 'patient_dashboard.html', {
        'doctors': doctors,
        'appointments': appointments
    })


@login_required
def book_appointment(request):
    doctors = Doctor.objects.all()

    if request.method == "POST":
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason = request.POST.get('reason')

        doctor = Doctor.objects.get(id=doctor_id)

        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason
        )

        messages.success(request, "Appointment booked successfully!")
        return redirect('patient_dashboard')  # 👈 Goes back to dashboard with the new appointment listed

    return render(request, 'book_appointment.html', {'doctors': doctors})

from django.utils import timezone
from datetime import timedelta

@login_required
def admin_dashboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)

    # Query counts
    today_appointments = Appointment.objects.filter(date=today).count()
    week_appointments = Appointment.objects.filter(date__range=[week_start, week_end]).count()
    upcoming_appointments = Appointment.objects.filter(date__gt=today).count()

    # List of today's appointments
    appointments_today = Appointment.objects.filter(date=today).order_by('time')

    context = {
        'today_appointments': today_appointments,
        'week_appointments': week_appointments,
        'upcoming_appointments': upcoming_appointments,
        'appointments_today': appointments_today,
    }
# data passed to the adminpage
    return render(request, 'admin_dashboard.html', context)

@login_required
def all_appointments(request):
    appointments = Appointment.objects.all().order_by('-date', 'time')
    return render(request, 'view_appointments.html', {'appointments': appointments})

def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        doctor_id = request.POST['doctor']
        appointment.doctor = Doctor.objects.get(id=doctor_id)
        appointment.date = request.POST['date']
        appointment.time = request.POST['time']
        appointment.reason = request.POST['reason']
        appointment.save()
        messages.success(request, "Appointment updated successfully!")
        return redirect('view_appointments')

    return render(request, 'edit_appointment.html', {'appointment': appointment, 'doctors': doctors})

def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    messages.success(request, "Appointment deleted.")
    return redirect('view_appointments')

#sql injection test
from django.db import connection


