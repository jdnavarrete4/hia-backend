from django.contrib import admin
from .models import Paciente, Medico, Administrador, Cita, HistorialMedico, Notificacion


class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'especialidad', 'correo_electronico', 'telefono')
    fields = ('nombre', 'apellido', 'especialidad', 'correo_electronico', 'telefono', 'contrasena')
    readonly_fields = ('contrasena',)  # Haz que el campo sea de solo lectura para que no sea visible en la vista de edición

    def save_model(self, request, obj, form, change):
        if 'contrasena' in form.changed_data:
            obj.contrasena = make_password(obj.contrasena)
        super().save_model(request, obj, form, change)

admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(Administrador)
admin.site.register(Cita)
admin.site.register(HistorialMedico)
admin.site.register(Notificacion)