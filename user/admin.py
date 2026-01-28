from django.contrib import admin
from .models import Doctor, Appointment

from .models import AuditLog

admin.site.register(Doctor)
admin.site.register(Appointment)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
    ordering = ('-timestamp',)  