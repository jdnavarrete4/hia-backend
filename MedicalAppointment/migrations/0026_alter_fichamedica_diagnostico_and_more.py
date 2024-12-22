from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('MedicalAppointment', '0025_alter_fichamedica_diagnostico_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichamedica',
            name='diagnostico',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fichas',
                to='MedicalAppointment.diagnostico',
                null=True,  # Permitir nulos temporalmente
            ),
        ),
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'MedicalAppointment_fichamedica' AND column_name = 'receta_id'
                ) THEN
                    ALTER TABLE "MedicalAppointment_fichamedica" ADD COLUMN "receta_id" integer;
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE MedicalAppointment_fichamedica DROP COLUMN receta_id;"
        ),
        migrations.AlterField(
            model_name='fichamedica',
            name='receta',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='MedicalAppointment.receta',
                null=False,  # No permitir nulos después de manejar registros existentes
            ),
        ),
        migrations.AlterField(
            model_name='fichamedica',
            name='fecha_creacion',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
