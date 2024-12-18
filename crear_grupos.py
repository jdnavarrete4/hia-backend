
import os
import django
import ftfy  # Librería para arreglar texto mal codificado

# Configurar Django para cargar el entorno correctamente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()



from django.contrib.auth.models import Group

# Crear los grupos
def crear_grupos():
    Group.objects.get_or_create(name='paciente')
    Group.objects.get_or_create(name='medico')
    Group.objects.get_or_create(name='administrador')
    print("Grupos creados correctamente")

if __name__ == '__main__':
    crear_grupos()