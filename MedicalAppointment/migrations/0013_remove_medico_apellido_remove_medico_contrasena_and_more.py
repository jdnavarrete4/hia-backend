# Generated by Django 4.2.3 on 2024-12-18 02:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MedicalAppointment', '0012_alter_medico_foto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medico',
            name='apellido',
        ),
        migrations.RemoveField(
            model_name='medico',
            name='contrasena',
        ),
        migrations.RemoveField(
            model_name='medico',
            name='correo_electronico',
        ),
        migrations.RemoveField(
            model_name='medico',
            name='nombre',
        ),
        migrations.RemoveField(
            model_name='medico',
            name='rol',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='apellido',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='contrasena',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='correo_electronico',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='nombre',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='rol',
        ),
        migrations.AddField(
            model_name='medico',
            name='user',
            field=models.OneToOneField(default=99, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
