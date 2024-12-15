import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')  # Cambia 'hospital_project' por el nombre de tu proyecto
django.setup()


from MedicalAppointment.models import Especialidad, Medico, Horario
from datetime import time

especialidades_horarios = [
    {
        "especialidad": "Medicina Interna",
        "dia_semana": "Lunes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
            {"hora_inicio": time(13, 0), "hora_fin": time(17, 0)}  # 1 PM - 5 PM
        ]
    },
    {
        "especialidad": "Traumatología",
        "dia_semana": "Martes",
        "horarios": [
            {"hora_inicio": time(9, 0), "hora_fin": time(13, 0)},  # 9 AM - 1 PM
            {"hora_inicio": time(14, 0), "hora_fin": time(18, 0)}  # 2 PM - 6 PM
        ]
    },
    {
        "especialidad": "Fisiatría",
        "dia_semana": "Miércoles",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
            {"hora_inicio": time(13, 0), "hora_fin": time(17, 0)}  # 1 PM - 5 PM
        ]
    },
    {
        "especialidad": "Psicología",
        "dia_semana": "Jueves",
        "horarios": [
            {"hora_inicio": time(9, 0), "hora_fin": time(13, 0)},  # 9 AM - 1 PM
            {"hora_inicio": time(14, 0), "hora_fin": time(18, 0)}  # 2 PM - 6 PM
        ]
    },
    {
        "especialidad": "Otorrinolaringología",
        "dia_semana": "Viernes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
            {"hora_inicio": time(13, 0), "hora_fin": time(17, 0)}  # 1 PM - 5 PM
        ]
    },
    {
        "especialidad": "Cirugía Plástica",
        "dia_semana": "Sábado",
        "horarios": [
            {"hora_inicio": time(9, 0), "hora_fin": time(13, 0)},  # 9 AM - 1 PM
        ]
    },
    {
        "especialidad": "Oftalmología",
        "dia_semana": "Lunes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
        ]
    },
    {
        "especialidad": "Dermatología",
        "dia_semana": "Martes",
        "horarios": [
            {"hora_inicio": time(14, 0), "hora_fin": time(18, 0)},  # 2 PM - 6 PM
        ]
    },
    {
        "especialidad": "Cardiología",
        "dia_semana": "Miércoles",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
            {"hora_inicio": time(13, 0), "hora_fin": time(17, 0)}  # 1 PM - 5 PM
        ]
    },
    {
        "especialidad": "Neurocirugía",
        "dia_semana": "Jueves",
        "horarios": [
            {"hora_inicio": time(9, 0), "hora_fin": time(13, 0)},  # 9 AM - 1 PM
        ]
    },
    {
        "especialidad": "Nefrología",
        "dia_semana": "Viernes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
        ]
    },
    {
        "especialidad": "Cirugía Pediátrica",
        "dia_semana": "Sábado",
        "horarios": [
            {"hora_inicio": time(9, 0), "hora_fin": time(13, 0)},  # 9 AM - 1 PM
        ]
    },
    {
        "especialidad": "Neonatología",
        "dia_semana": "Lunes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
        ]
    },
    {
        "especialidad": "Gastroenterología",
        "dia_semana": "Martes",
        "horarios": [
            {"hora_inicio": time(14, 0), "hora_fin": time(18, 0)},  # 2 PM - 6 PM
        ]
    },
    {
        "especialidad": "Obstetricia",
        "dia_semana": "Miércoles",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
        ]
    },
    {
        "especialidad": "Ginecología",
        "dia_semana": "Jueves",
        "horarios": [
            {"hora_inicio": time(13, 0), "hora_fin": time(17, 0)},  # 1 PM - 5 PM
        ]
    },
    {
        "especialidad": "Terapia Intensiva",
        "dia_semana": "Viernes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
        ]
    },
    {
        "especialidad": "Reumatología",
        "dia_semana": "Sábado",
        "horarios": [
            {"hora_inicio": time(9, 0), "hora_fin": time(13, 0)},  # 9 AM - 1 PM
        ]
    },
    {
        "especialidad": "Pediatría",
        "dia_semana": "Lunes",
        "horarios": [
            {"hora_inicio": time(8, 0), "hora_fin": time(12, 0)},  # 8 AM - 12 PM
        ]
    },
    {
        "especialidad": "Neumología",
        "dia_semana": "Martes",
        "horarios": [
            {"hora_inicio": time(14, 0), "hora_fin": time(18, 0)},  # 2 PM - 6 PM
        ]
    },
]

for especialidad_data in especialidades_horarios:
    try:
        especialidad = Especialidad.objects.get(nombre=especialidad_data['especialidad'])
        medicos = Medico.objects.filter(especialidad=especialidad)

        for idx, horario_data in enumerate(especialidad_data['horarios']):
            medico = medicos[idx % len(medicos)] if medicos else None  # Distribuir médicos
            Horario.objects.get_or_create(
                especialidad=especialidad,
                medico=medico,
                dia_semana=especialidad_data['dia_semana'],
                hora_inicio=horario_data['hora_inicio'],
                hora_fin=horario_data['hora_fin']
            )
        print(f"Horarios creados para {especialidad.nombre}")
    except Especialidad.DoesNotExist:
        print(f"Especialidad {especialidad_data['especialidad']} no encontrada.")