# Generated by Django 4.2.3 on 2024-12-14 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MedicalAppointment', '0005_provincia_canton'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='rol',
            field=models.CharField(choices=[('paciente', 'Paciente'), ('medico', 'Médico'), ('administrador', 'Administrador')], default='paciente', max_length=20),
        ),
    ]
