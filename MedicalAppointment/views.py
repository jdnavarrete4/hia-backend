# views.py
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Diagnostico, Enfermedad, Especialidad, Horario, Paciente, Medico,Administrador
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
from .serializers import CitaSerializer,DiagnosticoSerializer
from .models import Cita, FichaMedica




@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_paciente(request):
    if request.method == 'POST':
        data = request.data

        try:
            # Crear el usuario en el modelo User
            user = User.objects.create_user(
                username=data['correo_electronico'],  # El correo electrónico como nombre de usuario
                email=data['correo_electronico'],
                password=data['contrasena']
            )
            user.first_name = data['nombre']
            user.last_name = data['apellido']
            user.save()

            # Asignar el grupo "paciente" al usuario
            grupo_paciente = Group.objects.get(name='paciente')
            user.groups.add(grupo_paciente)

            # Crear el paciente asociado al usuario
            paciente = Paciente.objects.create(
                user=user,
                telefono=data['telefono'],
                numero_cedula=data['numero_cedula'],
                fecha_nacimiento=data['fecha_nacimiento'],
                direccion=data.get('direccion', "")  # Dirección opcional
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
            # Inicializar valores
            rol = 'desconocido'
            medico_id = None
            paciente_id = None

            # Determinar el rol del usuario basado en los grupos
            if user.groups.filter(name='paciente').exists():
                rol = 'paciente'
                # Obtener el ID del paciente asociado
                paciente = Paciente.objects.get(user=user)
                paciente_id = paciente.id
            elif user.groups.filter(name='medico').exists():
                rol = 'medico'
                # Obtener el ID del médico asociado
                medico = Medico.objects.get(user=user)
                medico_id = medico.id
            elif user.groups.filter(name='administrador').exists():
                rol = 'administrador'

            # Generar o recuperar el token
            token, _ = Token.objects.get_or_create(user=user)

            # Respuesta con token, rol e IDs adicionales según el caso
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'rol': rol,
                'token': token.key,
                'medico_id': medico_id,  # Solo para médicos
                'paciente_id': paciente_id  # Solo para pacientes
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'mensaje': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_data(request):
    try:
        # Obtener el modelo Paciente relacionado con el usuario autenticado
        paciente = request.user.paciente

        # Calcular la edad del paciente
        today = date.today()
        birth_date = paciente.fecha_nacimiento
        edad = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        # Determinar el rol del usuario desde los grupos
        if request.user.groups.filter(name='paciente').exists():
            rol = 'paciente'
        else:
            rol = 'desconocido'

        # Preparar los datos de respuesta
        data = {
            'id': paciente.id,
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'numero_cedula': paciente.numero_cedula,
            'correo_electronico': request.user.email,
            'telefono': paciente.telefono,
            'edad': edad,
            'rol': rol.capitalize()
        }
        return Response(data, status=200)

    except AttributeError:
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
    try:
        # Verificar que la especialidad existe
        especialidad_obj = Especialidad.objects.get(id=especialidad)

        # Filtrar médicos por la especialidad
        medicos = Medico.objects.filter(especialidad=especialidad_obj)

        # Preparar datos de respuesta
        data = [
            {
                'id': medico.id,
                'nombre': medico.user.first_name,
                'apellido': medico.user.last_name,
                'correo': medico.user.email,
                'telefono': medico.telefono,
                'descripcion': medico.descripcion,
                'foto': medico.foto if medico.foto else None
            }
            for medico in medicos
        ]

        return Response(data, status=200)

    except Especialidad.DoesNotExist:
        return Response({'error': 'Especialidad no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

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
        especialidad = Especialidad.objects.get(id=especialidad_id)
        horarios = Horario.objects.filter(especialidad_id=especialidad_id)

        fechas_disponibles = []
        hoy = datetime.today().date()
        fecha_final = hoy + timedelta(days=365)

        fecha_actual = hoy
        while fecha_actual <= fecha_final:
            
            dias_traduccion = {
            'monday': 'Lunes',
            'tuesday': 'Martes',
            'wednesday': 'Miércoles',
            'thursday': 'Jueves',
            'friday': 'Viernes',
            'saturday': 'Sábado',
            'sunday': 'Domingo',
                            }
            dia_semana = dias_traduccion.get(fecha_actual.strftime('%A').lower(), '')


            for horario in horarios.filter(dia_semana=dia_semana):
                medico_nombre = (
                    f"{horario.medico.user.first_name} {horario.medico.user.last_name}"
                    if horario.medico else "Sin asignar"
                )

                fechas_disponibles.append({
                    "fecha": fecha_actual.strftime('%d-%B-%Y'),
                    "dia_semana": horario.get_dia_semana_display(),
                    "hora_inicio": horario.hora_inicio.strftime('%H:%M'),
                    "hora_fin": horario.hora_fin.strftime('%H:%M'),
                    "medico": medico_nombre,
                    "medico_id": horario.medico.id if horario.medico else None,
                })

            fecha_actual += timedelta(days=1)

        paginator = CustomPagination()
        paginated_fechas = paginator.paginate_queryset(fechas_disponibles, request)
        return paginator.get_paginated_response(paginated_fechas)

    except Especialidad.DoesNotExist:
        return JsonResponse({"error": "Especialidad no encontrada."}, status=404)




from django.shortcuts import get_object_or_404

@api_view(['POST'])
def crear_cita(request):
    try:
        print("Datos recibidos en la API:", request.data)

        # Obtener datos del request
        paciente_id = request.data.get('paciente')  # Cambiar 'usuario' a 'paciente'
        especialidad_id = request.data.get('especialidad')
        medico_id = request.data.get('medico')
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')
        direccion = request.data.get('direccion')
        estado = request.data.get('estado', 'Reservada')

        # Validar campos obligatorios
        if not (paciente_id and especialidad_id and medico_id and fecha and hora):
            return Response({"error": "Faltan campos obligatorios en la solicitud."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener instancias de paciente, especialidad y médico
        paciente = get_object_or_404(Paciente, id=paciente_id)  # Ahora se usa `Paciente`
        especialidad = get_object_or_404(Especialidad, id=especialidad_id)
        medico = get_object_or_404(Medico, id=medico_id)

        # Crear la cita
        cita = Cita.objects.create(
            paciente=paciente,  # Asignar la instancia del paciente
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


@api_view(['POST'])
def crear_diagnostico(request, cita_id):
    try:
        cita = get_object_or_404(Cita, id=cita_id)
        data = request.data
        data['cita'] = cita.id

        serializer = DiagnosticoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
def finalizar_cita(request, cita_id):
    try:
        cita = get_object_or_404(Cita, id=cita_id)
        cita.estado = 'Finalizada'
        cita.save()

        return Response({"mensaje": "Cita finalizada con éxito."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def obtener_citas_medico(request, medico_id):
    try:
        medico = get_object_or_404(Medico, id=medico_id)
        citas = (
            Cita.objects
            .filter(medico=medico)
            .select_related('paciente__user', 'medico__user')  # <--- Cambiado
            .order_by('fecha', 'hora')
        )

        serializer = CitaSerializer(citas, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def listar_enfermedades(request):
    enfermedades = Enfermedad.objects.all()
    data = [{"id": enfermedad.id, "nombre": enfermedad.nombre} for enfermedad in enfermedades]
    return Response(data)

@api_view(['POST'])
def crear_ficha_medica(request, cita_id):
    try:
        # Obtener los datos de la cita
        cita = Cita.objects.get(id=cita_id)

        # Obtener datos del diagnóstico
        diagnostico_data = request.data.get('diagnostico')
        tipo_enfermedad = request.data.get('tipo_enfermedad')
        medicamentos = request.data.get('medicamentos')

        if not diagnostico_data or not tipo_enfermedad or not medicamentos:
            return Response({"error": "Faltan datos necesarios para crear la ficha médica."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el diagnóstico
        diagnostico = Diagnostico.objects.create(
            descripcion=diagnostico_data.get('descripcion'),
            es_covid=diagnostico_data.get('es_covid', False),
            medico=cita.medico,  # Asociar al médico de la cita
            paciente=cita.paciente  # Asociar al paciente de la cita
        )

        # Crear la ficha médica asociada al diagnóstico
        ficha_medica = FichaMedica.objects.create(
            cita=cita,
            diagnostico=diagnostico,  # Asociar el diagnóstico recién creado
            tipo_enfermedad=tipo_enfermedad,
            medicamentos=medicamentos
        )

        return Response({
            "mensaje": "Ficha médica creada exitosamente.",
            "ficha_id": ficha_medica.id
        }, status=status.HTTP_201_CREATED)

    except Cita.DoesNotExist:
        return Response({"error": "Cita no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
