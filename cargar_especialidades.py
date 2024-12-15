from MedicalAppointment.models import Especialidad

especialidades = [
    'Medicina Interna', 'Traumatología', 'Fisiatría', 'Psicología', 
    'Otorrinolaringología', 'Cirugía Plástica', 'Oftalmología', 
    'Dermatología', 'Cardiología', 'Neurocirugía', 'Nefrología',
    'Cirugía Pediátrica', 'Neonatología', 'Gastroenterología', 
    'Obstetricia', 'Ginecología', 'Terapia Intensiva', 
    'Reumatología', 'Pediatría', 'Neumología',
]

for nombre in especialidades:
    Especialidad.objects.get_or_create(nombre=nombre)

print("Especialidades cargadas correctamente.")