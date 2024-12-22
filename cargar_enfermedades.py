import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from MedicalAppointment.models import Enfermedad

enfermedades = [
    "Respiratorias", "Cardiovasculares", "Metabólicas y Endocrinas",
    "Infecciosas", "Gastrointestinales", "Neurológicas",
    "Psiquiátricas", "Dermatológicas", "Musculoesqueléticas",
    "Pediátricas", "Ginecológicas y Obstétricas", "Hematológicas",
    "Oncológicas", "Renales y Urológicas", "Oftalmológicas",
    "Reumatológicas", "Autoinmunes", "Genéticas",
    "Raras", "Otras  Comunes"
]

for enfermedad in enfermedades:
    Enfermedad.objects.create(nombre=enfermedad)

print("Enfermedades cargadas correctamente.")
