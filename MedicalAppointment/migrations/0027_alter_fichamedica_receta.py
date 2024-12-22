# Generated by Django 4.2.3 on 2024-12-22 01:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('MedicalAppointment', '0026_alter_fichamedica_diagnostico_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichamedica',
            name='receta',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, to='MedicalAppointment.receta'),
            preserve_default=False,
        ),
    ]
