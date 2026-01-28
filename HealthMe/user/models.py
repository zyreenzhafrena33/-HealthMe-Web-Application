from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.specialty}"


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment with {self.doctor.name} on {self.date} ({self.patient.username})"

def create_default_doctors(sender, **kwargs):
    from .models import Doctor
    if sender.name == 'user':  # make sure it runs only for your app
        default_doctors = [
            {'name': 'Dr. Aisha Rahman', 'specialty': 'Psychiatrist'},
            {'name': 'Dr. Daniel Lim', 'specialty': 'Clinical Psychologist'},
            {'name': 'Dr. Nurul Hana', 'specialty': 'Counselor'},
        ]
        for doc in default_doctors:
            Doctor.objects.get_or_create(name=doc['name'], specialty=doc['specialty'])

#sql injection testing
class TestPatient(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
