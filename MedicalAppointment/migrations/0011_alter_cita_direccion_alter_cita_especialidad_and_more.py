# Generated by Django 4.2.3 on 2024-12-15 01:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MedicalAppointment', '0010_remove_cita_motivo_remove_cita_paciente_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='direccion',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='cita',
            name='especialidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MedicalAppointment.especialidad'),
        ),
        migrations.AlterField(
            model_name='cita',
            name='hora',
            field=models.TimeField(default='09:00'),
        ),
        migrations.AlterField(
            model_name='cita',
            name='usuario',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
