# MedicalAppointment/urls.py
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views
from .views import citas_por_especialidad, crear_cita, fechas_disponibles_por_especialidad, horarios_disponibles, listar_medicos_por_especialidad, obtener_especialidades, obtener_provincias_y_cantones, registrar_paciente, login,get_patient_data
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'pacientes', api_views.PacienteViewSet)
router.register(r'medicos', api_views.MedicoViewSet)
router.register(r'administradores', api_views.AdministradorViewSet)
router.register(r'citas', api_views.CitaViewSet)
router.register(r'historiales', api_views.HistorialMedicoViewSet)
router.register(r'notificaciones', api_views.NotificacionViewSet)

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
  path('api/fechas-disponibles/<int:especialidad_id>/', fechas_disponibles_por_especialidad,name='fechas_disponibles_por_especialidad'),
  path('api/crear-cita/', crear_cita, name='crear_cita'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)