# views.py
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Especialidad, Horario, Paciente, Medico,Administrador
from .serializers import PacienteSerializer, MedicoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from datetime import date
from .models import Provincia
from datetime import timedelta, datetime
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from .serializers import CitaSerializer
from .models import Cita




@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_paciente(request):
    if request.method == 'POST':
        data = request.data

        # Crear el usuario en el modelo User
        try:
            user = User.objects.create_user(
                username=data['correo_electronico'],
                email=data['correo_electronico'],
                password=data['contrasena']
            )

            # Crear el paciente asociado al usuario
            paciente = Paciente.objects.create(
                user=user,
                nombre=data['nombre'],
                apellido=data['apellido'],
                telefono=data['telefono'],
                numero_cedula=data['numero_cedula'],
                correo_electronico=data['correo_electronico'], 
                fecha_nacimiento=data['fecha_nacimiento']
            )

            # Serializar el paciente para la respuesta
            serializer = PacienteSerializer(paciente)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    correo_electronico = request.data.get('correo_electronico')
    contrasena = request.data.get('contrasena')

    # Autenticar usando el modelo User
    user = authenticate(username=correo_electronico, password=contrasena)

    if user is not None:
        try:
            # Determinar el rol basado en el modelo relacionado
            if hasattr(user, 'paciente'):
                rol = 'paciente'
            elif hasattr(user, 'medico'):
                rol = 'medico'
            elif hasattr(user, 'administrador'):
                rol = 'administrador'
            else:
                rol = 'desconocido'

            # Generar o recuperar el token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'rol': rol,
                'token': token.key
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'mensaje': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_data(request):
    try:
        paciente = Paciente.objects.get(user=request.user)

        # Calcular la edad
        today = date.today()
        birth_date = paciente.fecha_nacimiento
        edad = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        data = {
            'id': paciente.id,  # Agrega el ID del paciente aquí
            'nombre': paciente.nombre,
            'apellido': paciente.apellido,
            'numero_cedula': paciente.numero_cedula,
            'correo_electronico': paciente.correo_electronico,
            'telefono': paciente.telefono,
            'edad': edad,
            'rol': paciente.rol.capitalize(),
        }
        return Response(data)
    except Paciente.DoesNotExist:
        return Response({'error': 'Paciente no encontrado'}, status=404)
    
@api_view(['GET'])
def obtener_provincias_y_cantones(request):
    data = [
        {
            'id': provincia.id,
            'nombre': provincia.nombre,
            'cantones': [{'id': canton.id, 'nombre': canton.nombre} for canton in provincia.cantones.all()]
        }
        for provincia in Provincia.objects.all()
    ]
    return Response(data)


@api_view(['GET'])
def obtener_especialidades(request):
    try:
        especialidades = Especialidad.objects.all()
        data = [{"id": especialidad.id, "nombre": especialidad.nombre} for especialidad in especialidades]
        return Response(data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
      
# Listar medico por especialidad
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_medicos_por_especialidad(request, especialidad):
    medicos = Medico.objects.filter(especialidad=especialidad)
    data = [
        {
            'id': medico.id,
            'nombre': medico.nombre,
            'apellido': medico.apellido,
            'correo': medico.correo_electronico,
            'telefono': medico.telefono,
            'descripcion': medico.descripcion,
            'foto': medico.foto.url if medico.foto else None
        }
        for medico in medicos
    ]
    return Response(data)

@api_view(['GET'])
def horarios_disponibles(request, especialidad_id):
    horarios = Horario.objects.filter(especialidad_id=especialidad_id)
    data = [
        {
            "dia_semana": horario.dia_semana,
            "hora_inicio": horario.hora_inicio.strftime('%H:%M'),
            "hora_fin": horario.hora_fin.strftime('%H:%M'),
            "medico": horario.medico.nombre if horario.medico else None,
        }
        for horario in horarios
    ]
    return Response(data)

@api_view(['GET'])
def citas_por_especialidad(request, especialidad_id, dia_semana):
    horarios = Horario.objects.filter(especialidad_id=especialidad_id, dia_semana=dia_semana)
    citas_disponibles = []

    for horario in horarios:
        hora_actual = datetime.combine(datetime.today(), horario.hora_inicio)
        hora_fin = datetime.combine(datetime.today(), horario.hora_fin)

        while hora_actual < hora_fin:
            citas_disponibles.append({
                "especialidad": horario.especialidad.nombre,
                "medico": horario.medico.nombre if horario.medico else None,
                "hora": hora_actual.strftime('%H:%M')
            })
            hora_actual += timedelta(hours=1)

    return Response(citas_disponibles)

class CustomPagination(PageNumberPagination):
    page_size = 10  # Resultados por página
    page_size_query_param = 'page_size'
    max_page_size = 50

@api_view(['GET'])
def fechas_disponibles_por_especialidad(request, especialidad_id):
    try:
        # Obtener la especialidad
        especialidad = Especialidad.objects.get(id=especialidad_id)
        
        # Obtener los horarios de la especialidad
        horarios = Horario.objects.filter(especialidad=especialidad)
        dias_semana = list(set(horario.get_dia_semana_display() for horario in horarios))  # Días únicos como texto

        # Mapeo de días de la semana en inglés a español
        dias_traduccion = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }

        # Fecha de inicio y final (un año a partir de hoy)
        hoy = datetime.today().date()
        fecha_final = hoy + timedelta(days=365)

        # Generar fechas disponibles
        fechas_disponibles = []
        fecha_actual = hoy

        while fecha_actual <= fecha_final:
            # Convertir el día de la semana actual a texto en español usando el diccionario
            dia_actual_texto = dias_traduccion.get(fecha_actual.strftime('%A'), '')
            print(f"Revisando fecha: {fecha_actual} ({dia_actual_texto})")
            if dia_actual_texto in dias_semana:  # Comparar con los días únicos del horario
                print(f"Fecha válida encontrada: {fecha_actual}")
                for horario in horarios.filter(dia_semana__iexact=dia_actual_texto):  # Filtrar horarios del día
                    fechas_disponibles.append({
                        "fecha": fecha_actual.strftime('%d-%B-%Y'),
                        "dia_semana": horario.get_dia_semana_display(),
                        "hora_inicio": horario.hora_inicio.strftime('%H:%M'),
                        "hora_fin": horario.hora_fin.strftime('%H:%M'),
                        "medico": horario.medico.nombre if horario.medico else "Sin asignar",
                        "medico_id": horario.medico.id if horario.medico else None,  # Agregar el ID del médico
                    })
            fecha_actual += timedelta(days=1)  # Incrementar un día
        
        paginator = CustomPagination()
        paginated_fechas = paginator.paginate_queryset(fechas_disponibles, request)
        return paginator.get_paginated_response(paginated_fechas)
    
    except Especialidad.DoesNotExist:
        print("Especialidad no encontrada.")
        return JsonResponse({"error": "Especialidad no encontrada."}, status=404)



from django.shortcuts import get_object_or_404

@api_view(['POST'])
def crear_cita(request):
    try:
        print("Datos recibidos en la API:", request.data)

        # Obtener datos del request
        usuario_id = request.data.get('usuario')
        especialidad_id = request.data.get('especialidad')
        medico_id = request.data.get('medico')
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')
        direccion = request.data.get('direccion')
        estado = request.data.get('estado', 'Reservada')

        # Validar campos obligatorios
        if not (usuario_id and especialidad_id and medico_id and fecha and hora):
            return Response({"error": "Faltan campos obligatorios en la solicitud."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener instancias de usuario, especialidad y médico
        usuario = get_object_or_404(User, id=usuario_id)  # Cambia a tu modelo si no es User
        especialidad = get_object_or_404(Especialidad, id=especialidad_id)
        medico = get_object_or_404(Medico, id=medico_id)

        # Crear la cita
        cita = Cita.objects.create(
            usuario=usuario,  # Asignar la instancia del usuario
            especialidad=especialidad,
            medico=medico,
            fecha=fecha,
            hora=hora,
            direccion=direccion,
            estado=estado,
        )

        # Serializar y retornar la cita creada
        serializer = CitaSerializer(cita)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("Error al crear la cita:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

