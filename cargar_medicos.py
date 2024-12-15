import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')  # Cambia 'hospital_project' por el nombre de tu proyecto
django.setup()

from MedicalAppointment.models import Especialidad, Medico

medicos = [
    {
        'nombre': 'Juan Diego',
        'apellido': 'Pérez',
        'especialidad': 'Medicina Interna',
        'correo_electronico': 'juan.perez@ejemplo.com',
        'telefono': '0987654301',
        'contrasena': 'contraseña_segura',
        'descripcion': 'Especialista en enfermedades internas.',
    },
    {
        'nombre': 'María Fernanda',
        'apellido': 'Gómez',
        'especialidad': 'Traumatología',
        'correo_electronico': 'maria.gomez@ejemplo.com',
        'telefono': '0987654302',
        'contrasena': 'otra_contraseña_segura',
        'descripcion': 'Especialista en lesiones óseas y musculares.',
    },
    {
        'nombre': 'Daniel Perez',
        'apellido': 'Jaramillo',
        'especialidad': 'Fisiatría',
        'correo_electronico': 'daniel.jaramillo@ejemplo.com',
        'telefono': '0987654303',
        'contrasena': 'contraseña_fuerte',
        'descripcion': 'Especialista en rehabilitación física.',
    },
    {
        'nombre': 'Lucía Martínez',
        'apellido': 'Torres',
        'especialidad': 'Psicología',
        'correo_electronico': 'lucia.martinez@ejemplo.com',
        'telefono': '0987654304',
        'contrasena': 'psicologia_segura',
        'descripcion': 'Especialista en psicoterapia y salud mental.',
    },
    {
        'nombre': 'Jorge Luis',
        'apellido': 'Sánchez',
        'especialidad': 'Otorrinolaringología',
        'correo_electronico': 'jorge.sanchez@ejemplo.com',
        'telefono': '0987654305',
        'contrasena': 'otorrino_segura',
        'descripcion': 'Especialista en problemas de oído, nariz y garganta.',
    },
    {
        'nombre': 'Ana Patricia',
        'apellido': 'Ramírez',
        'especialidad': 'Cirugía Plástica',
        'correo_electronico': 'ana.ramirez@ejemplo.com',
        'telefono': '0987654306',
        'contrasena': 'plastico_segura',
        'descripcion': 'Especialista en procedimientos estéticos.',
    },
    {
        'nombre': 'Pedro Javier',
        'apellido': 'Mendoza',
        'especialidad': 'Oftalmología',
        'correo_electronico': 'pedro.mendoza@ejemplo.com',
        'telefono': '0987654307',
        'contrasena': 'ojos_segura',
        'descripcion': 'Especialista en salud ocular.',
    },
    {
        'nombre': 'Gabriela Flores',
        'apellido': 'Castro',
        'especialidad': 'Dermatología',
        'correo_electronico': 'gabriela.flores@ejemplo.com',
        'telefono': '0987654308',
        'contrasena': 'piel_segura',
        'descripcion': 'Especialista en enfermedades de la piel.',
    },
    {
        'nombre': 'Fernando',
        'apellido': 'Rojas',
        'especialidad': 'Cardiología',
        'correo_electronico': 'fernando.rojas@ejemplo.com',
        'telefono': '0987654309',
        'contrasena': 'cardio_segura',
        'descripcion': 'Especialista en problemas cardíacos.',
    },
    {
        'nombre': 'Elena',
        'apellido': 'Guerrero',
        'especialidad': 'Neurocirugía',
        'correo_electronico': 'elena.guerrero@ejemplo.com',
        'telefono': '0987654310',
        'contrasena': 'neuro_segura',
        'descripcion': 'Especialista en cirugía cerebral.',
    },
    {
        'nombre': 'Victor Manuel',
        'apellido': 'Alvarado',
        'especialidad': 'Nefrología',
        'correo_electronico': 'victor.alvarado@ejemplo.com',
        'telefono': '0987654311',
        'contrasena': 'nefro_segura',
        'descripcion': 'Especialista en salud renal.',
    },
    {
        'nombre': 'Cecilia',
        'apellido': 'Rivas',
        'especialidad': 'Cirugía Pediátrica',
        'correo_electronico': 'cecilia.rivas@ejemplo.com',
        'telefono': '0987654312',
        'contrasena': 'pediatria_segura',
        'descripcion': 'Especialista en cirugía para niños.',
    },
    {
        'nombre': 'Mario',
        'apellido': 'Campos',
        'especialidad': 'Neonatología',
        'correo_electronico': 'mario.campos@ejemplo.com',
        'telefono': '0987654313',
        'contrasena': 'neo_segura',
        'descripcion': 'Especialista en cuidados neonatales.',
    },
    {
        'nombre': 'Julia',
        'apellido': 'Villalobos',
        'especialidad': 'Gastroenterología',
        'correo_electronico': 'julia.villalobos@ejemplo.com',
        'telefono': '0987654314',
        'contrasena': 'gastro_segura',
        'descripcion': 'Especialista en problemas gastrointestinales.',
    },
    {
        'nombre': 'Andrea',
        'apellido': 'Montenegro',
        'especialidad': 'Ginecología',
        'correo_electronico': 'andrea.montenegro@ejemplo.com',
        'telefono': '0987654315',
        'contrasena': 'gineco_segura',
        'descripcion': 'Especialista en salud femenina.',
    }
]

for medico_data in medicos:
    try:
        # Obtener la especialidad asociada
        especialidad = Especialidad.objects.get(nombre=medico_data['especialidad'])

        # Crear o actualizar el médico con los datos proporcionados
        medico, creado = Medico.objects.get_or_create(
            correo_electronico=medico_data['correo_electronico'],
            defaults={
                'nombre': medico_data['nombre'],
                'apellido': medico_data['apellido'],
                'especialidad': especialidad,
                'telefono': medico_data['telefono'],
                'contrasena': medico_data['contrasena'],  # Será encriptada por el modelo
                'descripcion': medico_data['descripcion'],
            },
        )
        if creado:
            print(f"Médico {medico.nombre} {medico.apellido} creado con éxito.")
        else:
            print(f"Médico {medico.nombre} {medico.apellido} ya existe.")
    except Especialidad.DoesNotExist:
        print(f"Error: La especialidad '{medico_data['especialidad']}' no existe. Verifica los nombres.")

print("Proceso de carga de médicos finalizado.")
