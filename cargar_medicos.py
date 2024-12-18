
import os
import django
import ftfy  


# Configurar Django para cargar el entorno correctamente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from MedicalAppointment.models import Medico, Especialidad
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password


# Función para arreglar texto
def fix_text(text):
    return ftfy.fix_text(text.strip())
   

medicos = [
    {
        'nombre': 'Juan Diego',
        'apellido': 'Pérez',
        'especialidad': 'Medicina Interna',
        'correo_electronico': 'juan.perez@ejemplo.com',
        'telefono': '0987654301',
        'contrasena': '2222',
        'descripcion': 'Especialista en enfermedades internas.',
        'foto': 'https://i.ibb.co/SRVH7Zv/Firefly-una-doctor-adulto-latino-de-piel-blanca-51830.jpg', 

    },
    {
        'nombre': 'María Fernanda',
        'apellido': 'Gómez',
        'especialidad': 'Traumatología',
        'correo_electronico': 'maria.gomez@ejemplo.com',
        'telefono': '0987654302',
        'contrasena': '2222',
        'descripcion': 'Especialista en lesiones óseas y musculares.',
        'foto': 'https://i.ibb.co/KbGLykx/Firefly-una-doctora-adulta-traumatologa-mujer-86017.jpg', 

    },
    {
        'nombre': 'Daniel Perez',
        'apellido': 'Jaramillo',
        'especialidad': 'Fisiatría',
        'correo_electronico': 'daniel.jaramillo@ejemplo.com',
        'telefono': '0987654303',
        'contrasena': '2222',
        'descripcion': 'Especialista en rehabilitación física.',
        'foto': 'https://i.ibb.co/3v01Rv4/Firefly-Doctor-feliz-98944.jpg', 

    },
    {
        'nombre': 'Lucía Martínez',
        'apellido': 'Torres',
        'especialidad': 'Psicología',
        'correo_electronico': 'lucia.martinez@ejemplo.com',
        'telefono': '0987654304',
        'contrasena': '2222',
        'descripcion': 'Especialista en psicoterapia y salud mental.',
        'foto': 'https://i.ibb.co/LhzFmnq/Firefly-una-doctora-adulta-de-piel-blanca-fisiatria-mujer-86017.jpg', 

    },
    {
        'nombre': 'Jorge Luis',
        'apellido': 'Sánchez',
        'especialidad': 'Otorrinolaringología',
        'correo_electronico': 'jorge.sanchez@ejemplo.com',
        'telefono': '0987654305',
        'contrasena': '2222',
        'descripcion': 'Especialista en problemas de oído, nariz y garganta.',
        'foto': 'https://i.ibb.co/z7vFSpk/Firefly-una-doctor-adulto-latino-de-piel-blanca-46632.jpg', 

    },
    {
        'nombre': 'Ana Patricia',
        'apellido': 'Ramírez',
        'especialidad': 'Cirugía Plástica',
        'correo_electronico': 'ana.ramirez@ejemplo.com',
        'telefono': '0987654306',
        'contrasena': '2222',
        'descripcion': 'Especialista en procedimientos estéticos.',
        'foto': 'https://i.ibb.co/LhzFmnq/Firefly-una-doctora-adulta-de-piel-blanca-fisiatria-mujer-86017.jpg', 

    },
    {
        'nombre': 'Pedro Javier',
        'apellido': 'Mendoza',
        'especialidad': 'Oftalmología',
        'correo_electronico': 'pedro.mendoza@ejemplo.com',
        'telefono': '0987654307',
        'contrasena': '2222',
        'descripcion': 'Especialista en salud ocular.',
        'foto': 'https://i.ibb.co/12X4nmT/Firefly-Doctor-latino-adulto-blanco-feliz-51830.jpg', 

    },
    {
        'nombre': 'Gabriela Flores',
        'apellido': 'Castro',
        'especialidad': 'Dermatología',
        'correo_electronico': 'gabriela.flores@ejemplo.com',
        'telefono': '0987654308',
        'contrasena': '2222',
        'descripcion': 'Especialista en enfermedades de la piel.',
        'foto': 'https://i.ibb.co/HB2xgsT/Firefly-una-doctora-adulta-traumatologa-mujer-86017.jpg', 

    },
    {
        'nombre': 'Fernando',
        'apellido': 'Rojas',
        'especialidad': 'Cardiología',
        'correo_electronico': 'fernando.rojas@ejemplo.com',
        'telefono': '0987654309',
        'contrasena': '2222',
        'descripcion': 'Especialista en problemas cardíacos.',
        'foto': 'https://i.ibb.co/3v01Rv4/Firefly-Doctor-feliz-98944.jpg', 

    },
    {
        'nombre': 'Elena',
        'apellido': 'Guerrero',
        'especialidad': 'Neurocirugía',
        'correo_electronico': 'elena.guerrero@ejemplo.com',
        'telefono': '0987654310',
        'contrasena': '2222',
        'descripcion': 'Especialista en cirugía cerebral.',
        'foto': 'https://i.ibb.co/LhzFmnq/Firefly-una-doctora-adulta-de-piel-blanca-fisiatria-mujer-86017.jpg', 

    },
    {
        'nombre': 'Victor Manuel',
        'apellido': 'Alvarado',
        'especialidad': 'Nefrología',
        'correo_electronico': 'victor.alvarado@ejemplo.com',
        'telefono': '0987654311',
        'contrasena': '2222',
        'descripcion': 'Especialista en salud renal.',
        'foto': 'https://i.ibb.co/12X4nmT/Firefly-Doctor-latino-adulto-blanco-feliz-51830.jpg', 

    },
    {
        'nombre': 'Cecilia',
        'apellido': 'Rivas',
        'especialidad': 'Cirugía Pediátrica',
        'correo_electronico': 'cecilia.rivas@ejemplo.com',
        'telefono': '0987654312',
        'contrasena': '2222',
        'descripcion': 'Especialista en cirugía para niños.',
        'foto': 'https://i.ibb.co/LhzFmnq/Firefly-una-doctora-adulta-de-piel-blanca-fisiatria-mujer-86017.jpg', 

    },
    {
        'nombre': 'Mario',
        'apellido': 'Campos',
        'especialidad': 'Neonatología',
        'correo_electronico': 'mario.campos@ejemplo.com',
        'telefono': '0987654313',
        'contrasena': '2222',
        'descripcion': 'Especialista en cuidados neonatales.',
        'foto': 'https://i.ibb.co/3v01Rv4/Firefly-Doctor-feliz-98944.jpg', 

    },
    {
        'nombre': 'Julia',
        'apellido': 'Villalobos',
        'especialidad': 'Gastroenterología',
        'correo_electronico': 'julia.villalobos@ejemplo.com',
        'telefono': '0987654314',
        'contrasena': '2222',
        'descripcion': 'Especialista en problemas gastrointestinales.',
        'foto': 'https://i.ibb.co/HB2xgsT/Firefly-una-doctora-adulta-traumatologa-mujer-86017.jpg', 

    },
    {
        'nombre': 'Andrea',
        'apellido': 'Montenegro',
        'especialidad': 'Ginecología',
        'correo_electronico': 'andrea.montenegro@ejemplo.com',
        'telefono': '0987654315',
        'contrasena': '2222',
        'descripcion': 'Especialista en salud femenina.',
        'foto': 'https://i.ibb.co/LhzFmnq/Firefly-una-doctora-adulta-de-piel-blanca-fisiatria-mujer-86017.jpg', 

    }
]

for medico_data in medicos:
    try:
        # Buscar o crear la especialidad
        especialidad_nombre = fix_text(medico_data['especialidad'])
        especialidad, _ = Especialidad.objects.get_or_create(nombre=especialidad_nombre)

        # Crear el usuario en el modelo User
        user, created = User.objects.get_or_create(
            username=medico_data['correo_electronico'],
            defaults={
                'first_name': fix_text(medico_data['nombre']),
                'last_name': fix_text(medico_data['apellido']),
                'email': medico_data['correo_electronico'],
                'password': make_password(medico_data['contrasena']),
            }
        )

        # Asignar el grupo 'medico' al usuario
        grupo_medico, _ = Group.objects.get_or_create(name='medico')
        user.groups.add(grupo_medico)

        # Crear o actualizar el médico asociado
        medico, creado = Medico.objects.update_or_create(
            user=user,  # Relación con User
            defaults={
                'especialidad': especialidad,
                'telefono': medico_data['telefono'],
                'descripcion': fix_text(medico_data['descripcion']),
                'foto': medico_data['foto'],
            },
        )

        if creado:
            print(f"✅ Médico {user.first_name} {user.last_name} creado con éxito.")
        else:
            print(f"🔄 Médico {user.first_name} {user.last_name} actualizado con éxito.")

    except Exception as e:
        print(f"❌ Error al procesar el médico {medico_data['nombre']} {medico_data['apellido']}: {e}")

print("🚀 Proceso de carga de médicos finalizado.")