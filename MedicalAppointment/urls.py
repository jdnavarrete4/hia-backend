from django import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar vistas y módulos necesarios
from . import api_views
from .views import (
    citas_por_especialidad,
    crear_cita,
    crear_diagnostico,
    crear_ficha_medica,
    crear_receta,
    fechas_disponibles_por_especialidad,
    horarios_disponibles,
    listar_enfermedades,
    listar_medicos_por_especialidad,
    obtener_especialidades,
    obtener_provincias_y_cantones,
    registrar_paciente,
    login,
    get_patient_data,
    obtener_citas_medico,  # Asegúrate de importar la vista correcta
)

# Configuración del router
router = DefaultRouter()
router.register(r'pacientes', api_views.PacienteViewSet)
router.register(r'medicos', api_views.MedicoViewSet)
router.register(r'administradores', api_views.AdministradorViewSet)
router.register(r'citas', api_views.CitaViewSet)
router.register(r'historiales', api_views.HistorialMedicoViewSet)
router.register(r'notificaciones', api_views.NotificacionViewSet)

# URLs principales
urlpatterns = [
    path('api/', include(router.urls)),
    path('register/', registrar_paciente, name='registrar_paciente'),
    path('login/', login, name='login'),
    path('api/patient-data/', get_patient_data, name='get_patient_data'),
    path('api/provincias-cantones/', obtener_provincias_y_cantones, name='provincias-cantones'),
    path('api/especialidades/', obtener_especialidades, name='obtener_especialidades'),
    path('api/medicos/<str:especialidad>/', listar_medicos_por_especialidad, name='listar_medicos_por_especialidad'),
    path('api/horarios-disponibles/<int:especialidad_id>/', horarios_disponibles, name='horarios_disponibles'),
    path('citas-disponibles/<int:especialidad_id>/<str:dia_semana>/', citas_por_especialidad, name='citas_disponibles'),
    path('api/fechas-disponibles/<int:especialidad_id>/', fechas_disponibles_por_especialidad, name='fechas_disponibles_por_especialidad'),
    path('api/crear-cita/', crear_cita, name='crear_cita'),
    path('api/medico/<int:medico_id>/citas/', obtener_citas_medico, name='obtener_citas_medico'),  
    path('api/enfermedades/', listar_enfermedades, name='listar_enfermedades'),
    path('api/fichas-medicas/', crear_ficha_medica, name='crear_ficha_medica'),
    path('api/diagnosticos/<int:cita_id>/', crear_diagnostico, name='crear_diagnostico'),
    path('api/recetas/', crear_receta, name='crear_receta'),


]

# Configuración de media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
