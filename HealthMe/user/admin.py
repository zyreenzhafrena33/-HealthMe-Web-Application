from django.contrib import admin
from .models import Doctor, Appointment
from .models import TestPatient

admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(TestPatient)
