# Generated by Django 4.2.3 on 2024-12-16 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MedicalAppointment', '0011_alter_cita_direccion_alter_cita_especialidad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medico',
            name='foto',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
