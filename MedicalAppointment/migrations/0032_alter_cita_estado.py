# Generated by Django 4.2.3 on 2024-12-22 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MedicalAppointment', '0031_remove_fichamedica_tipo_enfermedad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('reservada', 'Reservada'), ('cancelada', 'Cancelada'), ('finalizada', 'Finalizada')], default='reservada', max_length=50),
        ),
    ]
