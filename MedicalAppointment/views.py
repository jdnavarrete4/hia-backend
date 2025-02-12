# views.py
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Diagnostico, Enfermedad, Especialidad, Horario, Paciente, Medico,Administrador, Canton
from .serializers import PacienteSerializer, MedicoSerializer, RecetaSerializer
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
from datetime import datetime, timedelta
import pytz
import calendar 
from django.db.models import Count, Q, F
from django.db.models import Avg
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from rest_framework.generics import ListAPIView
from django.db.models.functions import Concat
from django.db.models import Value

def calcular_triaje(fc, fr, pa, spo2, nc):
    puntaje_total = 0

    # Frecuencia cardiaca
    if fc and '-' in fc:
        rango = [int(x) for x in fc.split('-')]
        if rango[0] < 40 or rango[1] > 140:
            puntaje_total += 5 # critica
        elif 121 <= rango[1] <= 140 or 40 <= rango[0] <= 59:
            puntaje_total += 3# severa
        elif 100 <= rango[1] <= 120 or 50 <= rango[0] <= 59:
            puntaje_total += 1# moderada

    # Frecuencia respiratoria
    if fr:
        fr = int(fr)
        if fr > 30 or fr < 6:
            puntaje_total += 5
        elif 25 <= fr <= 30 or 6 <= fr <= 8:
            puntaje_total += 3
        elif 21 <= fr <= 24 or 9 <= fr <= 11:
            puntaje_total += 1

    # Presión arterial 
    if pa:
        pa = int(pa)
        if pa > 180 or pa < 70:
            puntaje_total += 5
        elif 161 <= pa <= 180 or 70 <= pa <= 79:
            puntaje_total += 3
        elif 140 <= pa <= 160 or 80 <= pa <= 89:
            puntaje_total += 1

    # Saturación de oxígeno
    if spo2:
        spo2 = float(spo2)
        if spo2 < 85:
            puntaje_total += 5
        elif 85 <= spo2 < 90:
            puntaje_total += 3
        elif 90 <= spo2 < 95:
            puntaje_total += 1

    # Nivel de conciencia
    if nc == 'no_responde':
        puntaje_total += 5
    elif nc == 'dolor':
        puntaje_total += 3
    elif nc == 'voz':
        puntaje_total += 1

    # Categoría final
    if puntaje_total <= 4:
        categoria = 'Normal'
    elif 5 <= puntaje_total <= 9:
        categoria = 'Alerta moderada'
    elif 10 <= puntaje_total <= 14:
        categoria = 'Alerta severa'
    else:
        categoria = 'Crítico'

    return puntaje_total, categoria


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

          # Validar la provincia seleccionada
            provincia = Provincia.objects.get(id=data['provincia'])

            # Si la provincia es "Otro" (ID 25), usar el país proporcionado y no vincular a cantón
            if provincia.id == 26:
                pais = data.get('pais')  # El país ingresado por el usuario
                if not pais:
                    return Response({'error': 'Debe proporcionar un país cuando la provincia sea "Otro".'}, status=status.HTTP_400_BAD_REQUEST)
                canton = None  # No se asigna ningún cantón
            else:
                # Validar que el cantón exista y pertenezca a la provincia seleccionada
                canton = Canton.objects.get(id=data['canton'])
                pais = "Ecuador"  # No se usa el campo país si no es "Otro"

             # Validar tipo de identificación
            if data['tipo_identificacion'] not in ['cedula', 'pasaporte']:
                return Response({'error': 'Tipo de identificación no válido. Debe ser "cedula" o "pasaporte".'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear el paciente asociado al usuario
            paciente = Paciente.objects.create(
                user=user,
                telefono=data['telefono'],
                tipo_identificacion=data['tipo_identificacion'],  # Nuevo campo
                numero_identificacion=data['numero_identificacion'],  # Nuevo campo
                fecha_nacimiento=data['fecha_nacimiento'],
                direccion=data.get('direccion', ""),  # Dirección opcional
                provincia=provincia,
                canton=canton,
                genero=data['genero'],
                pais=pais
            )

            # Serializar el paciente para la respuesta
            serializer = PacienteSerializer(paciente)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Provincia.DoesNotExist:
            return Response({'error': 'La provincia especificada no existe.'}, status=status.HTTP_400_BAD_REQUEST)
        except Canton.DoesNotExist:
            return Response({'error': 'El cantón especificado no existe o no pertenece a la provincia.'}, status=status.HTTP_400_BAD_REQUEST)
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
            'numero_identificacion': paciente.numero_identificacion,
            'correo_electronico': request.user.email,
            'telefono': paciente.telefono,
            'tipo_identificacion': paciente.tipo_identificacion,
            'edad': edad,
            'rol': rol.capitalize(),
            'genero': paciente.genero
        }
        return Response(data, status=200)

    except AttributeError:
        return Response({'error': 'Paciente no encontrado'}, status=404)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_data(request):
    try:
        # Obtener el modelo Médico relacionado con el usuario autenticado
        medico = request.user.medico

        # Determinar el rol del usuario desde los grupos
        if request.user.groups.filter(name='medico').exists():
            rol = 'medico'
        else:
            rol = 'desconocido'

        # Preparar los datos de respuesta
        data = {
            'id': medico.id,
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'especialidad': medico.especialidad.nombre,  # Ajusta según tu modelo
            'correo_electronico': request.user.email,
            'telefono': medico.telefono,  # Si tienes un campo para teléfono
            'rol': rol.capitalize(),
        }

        return Response(data, status=200)

    except AttributeError:
        return Response({'error': 'Médico no encontrado'}, status=404)
    
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

from django.db.models import Q

from django.db.models import Q

@api_view(['GET'])
def fechas_disponibles_por_especialidad(request, especialidad_id):
    try:
        # Zona horaria de Ecuador
        ecuador_tz = pytz.timezone("America/Guayaquil")
        ahora = datetime.now(ecuador_tz)  # Obtener la fecha y hora actual en Ecuador

        especialidad = Especialidad.objects.get(id=especialidad_id)
        horarios = Horario.objects.filter(especialidad_id=especialidad_id)

        # Obtener las citas reservadas o finalizadas
        citas_ocupadas = Cita.objects.filter(
            especialidad=especialidad,
            estado__in=['Reservada', 'finalizada']
        )

        # Obtener parámetros de rango de fechas
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse(
                    {"error": "Formato de fecha no válido. Use 'YYYY-MM-DD'."},
                    status=400
                )
        else:
            # Si no se proporcionan fechas, usar rango predeterminado de un año
            start_date = ahora.date()
            end_date = start_date + timedelta(days=365)

        # Diccionario para consolidar fechas y horarios
        fechas_agrupadas = {}

        fecha_actual = start_date
        while fecha_actual <= end_date:
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

            horarios_dia = horarios.filter(dia_semana=dia_semana)

            # Crear un conjunto de horas ocupadas para esta fecha
            horas_ocupadas = set(
                cita.hora.strftime('%H:%M') for cita in citas_ocupadas.filter(fecha=fecha_actual)
            )

            for horario in horarios_dia:
                # Generar las horas dentro del rango del horario
                hora_actual = datetime.combine(fecha_actual, horario.hora_inicio, tzinfo=ecuador_tz)
                hora_fin = datetime.combine(fecha_actual, horario.hora_fin, tzinfo=ecuador_tz)

                horas_disponibles = []
                while hora_actual < hora_fin:
                    hora_str = hora_actual.strftime('%H:%M')

                    # Verificar que la hora no esté ocupada y no sea anterior a la hora actual
                    if hora_str not in horas_ocupadas and (
                        fecha_actual > ahora.date() or hora_actual.time() > ahora.time()
                    ):
                        horas_disponibles.append(hora_str)

                    hora_actual += timedelta(hours=1)

                if horas_disponibles:  # Solo agregar si hay horas disponibles
                    medico_nombre = (
                        f"{horario.medico.user.first_name} {horario.medico.user.last_name}"
                        if horario.medico else "Sin asignar"
                    )

                    # Consolidar horarios por fecha
                    if fecha_actual not in fechas_agrupadas:
                        fechas_agrupadas[fecha_actual] = {
                            "fecha": fecha_actual.strftime('%d-%B-%Y'),
                            "dia_semana": dia_semana,
                            "horarios": horas_disponibles,
                            "medico": medico_nombre,
                            "medico_id": horario.medico.id if horario.medico else None,
                        }
                    else:
                        # Agregar más horarios a la misma fecha
                        fechas_agrupadas[fecha_actual]["horarios"].extend(horas_disponibles)

            fecha_actual += timedelta(days=1)

        # Convertir el diccionario a una lista
        fechas_disponibles = list(fechas_agrupadas.values())

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
        # Obtén la cita asociada al diagnóstico
        cita = get_object_or_404(Cita, id=cita_id)

        # Datos enviados por el médico
        datos = request.data
        descripcion = datos.get('descripcion', '')
        es_covid = datos.get('es_covid', False)
        enfermedad_id = datos.get('enfermedad')
        frecuencia_cardiaca = datos.get('frecuencia_cardiaca')
        frecuencia_respiratoria = datos.get('frecuencia_respiratoria')
        presion_arterial = datos.get('presion_arterial')
        saturacion_oxigeno = datos.get('saturacion_oxigeno')
        nivel_conciencia = datos.get('nivel_conciencia')

        # Validar que la enfermedad exista
        enfermedad = get_object_or_404(Enfermedad, id=enfermedad_id)

        # Calcular puntaje total y categoría
        puntaje_total, categoria_triaje = calcular_triaje(
            frecuencia_cardiaca,
            frecuencia_respiratoria,
            presion_arterial,
            saturacion_oxigeno,
            nivel_conciencia
        )

        # Crear el diagnóstico
        diagnostico = Diagnostico.objects.create(
            descripcion=descripcion,
            es_covid=es_covid,
            medico=cita.medico.user,
            paciente=cita.paciente,
            enfermedad=enfermedad,
            frecuencia_cardiaca=frecuencia_cardiaca,
            frecuencia_respiratoria=frecuencia_respiratoria,
            presion_arterial=presion_arterial,
            saturacion_oxigeno=saturacion_oxigeno,
            nivel_conciencia=nivel_conciencia,
            puntaje_total=puntaje_total,
            categoria_triaje=categoria_triaje
        )

        # Responder con el resultado
        return Response({
            "id": diagnostico.id,
            "descripcion": diagnostico.descripcion,
            "puntaje_total": diagnostico.puntaje_total,
            "categoria_triaje": diagnostico.categoria_triaje,
            "detalles": {
                "frecuencia_cardiaca": diagnostico.frecuencia_cardiaca,
                "frecuencia_respiratoria": diagnostico.frecuencia_respiratoria,
                "presion_arterial": diagnostico.presion_arterial,
                "saturacion_oxigeno": diagnostico.saturacion_oxigeno,
                "nivel_conciencia": diagnostico.nivel_conciencia,
            }
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Receta, Diagnostico
from .serializers import RecetaSerializer

@api_view(['POST'])
def crear_receta(request):
    try:
        diagnostico_id = request.data.get('diagnostico_id')
        medicamentos = request.data.get('medicamentos', [])
        notas = request.data.get('notas', "")

        # Validar si el diagnóstico existe
        diagnostico = Diagnostico.objects.get(id=diagnostico_id)

        # Crear cada medicamento como una entrada de receta
        recetas_creadas = []
        for medicamento in medicamentos:
            receta = Receta.objects.create(
                diagnostico=diagnostico,
                nombre_medicamento=medicamento.get('nombre_medicamento', ""),
                dosis=medicamento.get('dosis', "No especificada"),
                duracion=medicamento.get('duracion', "No especificada"),
                prescripcion=medicamento.get('prescripcion', ""),
                notas=notas,
            )
            recetas_creadas.append(receta)

        # Serializar y retornar la primera receta creada como respuesta
        serializer = RecetaSerializer(recetas_creadas, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Diagnostico.DoesNotExist:
        return Response({"error": "El diagnóstico no existe."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
def crear_ficha_medica(request):
    try:
        cita_id = request.data.get('cita_id')
        diagnostico_id = request.data.get('diagnostico_id')
        receta_id = request.data.get('receta_id')

        cita = get_object_or_404(Cita, id=cita_id)
        diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id)
        receta = get_object_or_404(Receta, id=receta_id)

        ficha_medica = FichaMedica.objects.create(
            cita=cita,
            diagnostico=diagnostico,
            receta=receta,
        )

        cita.estado = 'finalizada'
        cita.save()

        return Response({"id": ficha_medica.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_covid(request):
    try:
  
        intervalo = request.query_params.get('intervalo', 'mes')  

        # Fecha actual
        hoy = date.today()

        # Filtrar las fechas según el intervalo
        if intervalo == 'semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de la semana actual
            fin_semana = inicio_semana + timedelta(days=6)  # Domingo de la semana actual
            fichas_covid = FichaMedica.objects.filter(
                diagnostico__es_covid=True,
                cita__fecha__range=(inicio_semana, fin_semana)
            )
            trunc_function = TruncDay  # Agrupar por día dentro de la semana
        elif intervalo == 'mes':
            inicio_mes = hoy.replace(day=1)  # Primer día del mes actual
            fin_mes = (hoy.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1) 
            fichas_covid = FichaMedica.objects.filter(
                diagnostico__es_covid=True,
                cita__fecha__range=(inicio_mes, fin_mes)
            )
            trunc_function = TruncDay  # Agrupar por día dentro del mes
        elif intervalo == 'anio':  # Caso para año
            inicio_anio = hoy.replace(month=1, day=1)  # Primer día del año actual
            fin_anio = hoy.replace(month=12, day=31)  # Último día del año actual
            fichas_covid = FichaMedica.objects.filter(
                diagnostico__es_covid=True,
                cita__fecha__year=hoy.year
            )
            trunc_function = TruncMonth  # Agrupar por mes dentro del año
        else:
            # Intervalo por día (hoy)
            fichas_covid = FichaMedica.objects.filter(
                diagnostico__es_covid=True,
                cita__fecha=hoy
            )
            trunc_function = TruncDay

        # Agrupar por el intervalo seleccionado
        estadisticas = (
            fichas_covid.annotate(intervalo=trunc_function('cita__fecha'))
            .values('intervalo', 'cita__paciente__genero')
            .annotate(total=Count('id'))
            .order_by('intervalo')
        )

        # Formatear los datos para la respuesta
        data = {}
        for item in estadisticas:
            intervalo_valor = item["intervalo"]
            genero = item["cita__paciente__genero"]
            total = item["total"]

            if intervalo == 'anio':  # Mostrar el nombre del mes en lugar de la fecha
                fecha = calendar.month_name[intervalo_valor.month]  # Obtiene el nombre del mes
            else:
                fecha = intervalo_valor  # Mantener la fecha original para día/semana/mes

            if fecha not in data:
                data[fecha] = {"fecha": fecha, "hombres": 0, "mujeres": 0}

            if genero == 'Masculino':
                data[fecha]["hombres"] += total
            elif genero == 'Femenino':
                data[fecha]["mujeres"] += total

        # Convertir el diccionario a una lista
        resultado = list(data.values())

        # Verificar si no hay datos
        if not resultado:
            return Response({"message": "No existen datos para la fecha seleccionada."}, status=404)

        return Response(resultado, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def estadisticas_por_provincia(request):
    try:
        # Agrupar por provincia y género
        datos = (
            Paciente.objects.values('provincia__nombre', 'genero')
            .annotate(total=Count('id'))
            .order_by('provincia__nombre')
        )

        # Estructurar los datos para el frontend
        provincias = {}
        for dato in datos:
            provincia = dato['provincia__nombre']
            genero = dato['genero']
            total = dato['total']

            if provincia not in provincias:
                provincias[provincia] = {'hombres': 0, 'mujeres': 0}

            if genero == 'Masculino':
                provincias[provincia]['hombres'] += total
            elif genero == 'Femenino':
                provincias[provincia]['mujeres'] += total

        # Calcular el total global
        total_global = sum(
            provincia['hombres'] + provincia['mujeres'] for provincia in provincias.values()
        )

        # Formatear respuesta
        respuesta = [
            {
                'provincia': provincia,
                'hombres': data['hombres'],
                'mujeres': data['mujeres'],
                'porcentaje': round(
                    ((data['hombres'] + data['mujeres']) / total_global) * 100, 1
                )
            }
            for provincia, data in provincias.items()
        ]

        return Response({
            'total_global': total_global,
            'datos': respuesta
        }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
def estadisticas_por_especialidad(request):
    try:
        # Agrupar citas finalizadas por especialidad
        datos = (
            Cita.objects.filter(estado__in=['Reservada', 'finalizada'])
            .values('especialidad__nombre')
            .annotate(total=Count('id'))
            .order_by('-total')  
        )

        # Total global de citas
        total_global = sum(d['total'] for d in datos)

        # Formatear respuesta
        respuesta = {
            'total_global': total_global,
            'datos': [
                {
                    'especialidad': dato['especialidad__nombre'],
                    'total': dato['total'],
                    'porcentaje': round((dato['total'] / total_global) * 100, 2)
                }
                for dato in datos
            ]
        }

        return Response(respuesta, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
def enfermedades_mas_comunes(request):
    try:
        # Contar diagnósticos agrupados por enfermedad
        datos = (
            Diagnostico.objects.values('enfermedad__nombre')
            .annotate(total=Count('id'))
            .order_by('-total')  
        )

        # Total de diagnósticos
        total_global = sum(d['total'] for d in datos)

        # Formatear respuesta
        respuesta = {
            'total_global': total_global,
            'datos': [
                {
                    'enfermedad': dato['enfermedad__nombre'],
                    'total': dato['total']
                }
                for dato in datos
            ]
        }

        return Response(respuesta, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_citas_paciente(request):
    try:
        # Obtener el paciente autenticado
        paciente = request.user.paciente

        citas = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora')

        data = []
        for cita in citas:
            diagnostico_detalle = None
            recetas_detalle = []

            if cita.estado == 'finalizada':
                ficha_medica = getattr(cita, 'ficha_medica', None)
                if ficha_medica and ficha_medica.diagnostico:
                    diagnostico = ficha_medica.diagnostico
                    diagnostico_detalle = {
                        "descripcion": diagnostico.descripcion,
                        "es_covid": diagnostico.es_covid,
                        "enfermedad": diagnostico.enfermedad.nombre if diagnostico.enfermedad else None
                    }

                    # Obtener todas las recetas asociadas al diagnóstico
                    recetas = diagnostico.recetas.all()
                    recetas_detalle = [
                        {
                            "nombre_medicamento": receta.nombre_medicamento,
                            "dosis": receta.dosis,
                            "duracion": receta.duracion,
                            "prescripcion": receta.prescripcion,
                        }
                        for receta in recetas
                    ]

            # Agregar los datos de la cita a la respuesta
            data.append({
                'id': cita.id,
                'fecha': cita.fecha.strftime('%d-%m-%Y'),
                'hora': cita.hora.strftime('%H:%M'),
                'estado': cita.estado,
                'especialidad': cita.especialidad.nombre,
                'medico': f"{cita.medico.user.first_name} {cita.medico.user.last_name}",
                'direccion': cita.direccion,
                'calificacion': cita.calificacion,
                'diagnostico': diagnostico_detalle,  # Solo para finalizadas
                'recetas': recetas_detalle,         # Lista de medicamentos
            })

        return Response(data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calificar_cita(request, cita_id):
    try:
        cita = get_object_or_404(Cita, id=cita_id, paciente__user=request.user)

        if cita.estado != 'finalizada':
            return Response({'error': 'Solo se pueden calificar citas finalizadas.'}, status=400)

        calificacion = request.data.get('calificacion')
        if not (1 <= int(calificacion) <= 5):
            return Response({'error': 'La calificación debe estar entre 1 y 5.'}, status=400)

        cita.calificacion = calificacion
        cita.save()

        return Response({'mensaje': 'Cita calificada con éxito.'}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def estadisticas_eficiencia(request):
    try:
        # Calcular eficiencia por especialidad
        especialidades = (
            Cita.objects.filter(calificacion__isnull=False)
            .values('especialidad__nombre')
            .annotate(eficiencia=Avg('calificacion'))
            .order_by('-eficiencia')
        )
        especialidades_data = [
            {"nombre": item['especialidad__nombre'], "eficiencia": round(item['eficiencia'], 2)}
            for item in especialidades
        ]

        # Calcular eficiencia por médico
        medicos = (
            Cita.objects.filter(calificacion__isnull=False)
            .values('medico__user__first_name', 'medico__user__last_name')
            .annotate(eficiencia=Avg('calificacion'))
            .order_by('-eficiencia')
        )
        medicos_data = [
            {
                "nombre": f"{item['medico__user__first_name']} {item['medico__user__last_name']}",
                "eficiencia": round(item['eficiencia'], 2),
            }
            for item in medicos
        ]

        # Devolver los datos en un solo JSON
        return Response({
            "especialidades": especialidades_data,
            "medicos": medicos_data,
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_paciente(request):
    """
    Permite a un médico buscar y ver las citas de cualquier paciente
    ingresando el número de cédula, nombre o apellido.
    """
    try:
        # Validar que el usuario autenticado tiene el rol de médico
        if not request.user.groups.filter(name='medico').exists():
            return Response({"error": "Solo los médicos pueden acceder a esta información."}, status=403)

        # Obtener el parámetro de búsqueda (cédula, nombre o apellido)
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"error": "Debe proporcionar un parámetro de búsqueda ''."}, status=400)

        # Buscar pacientes que coincidan con el criterio
        pacientes = Paciente.objects.filter(
            Q(numero_identificacion__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) | 
            Q(user__first_name__icontains=query) &  Q(user__last_name__icontains=query)
        )
        pacientes = Paciente.objects.annotate(
    full_name=Concat('user__first_name', Value(' '), 'user__last_name')
    ).filter(
    Q(numero_identificacion__icontains=query) |  # Buscar por número de identificación
    Q(user__first_name__icontains=query) |      # Buscar por nombre
    Q(user__last_name__icontains=query) |       # Buscar por apellido
    Q(full_name__icontains=query)               # Buscar por combinación de nombre y apellido
        )

        # Verificar si se encontraron pacientes
        if not pacientes.exists():
            return Response({"error": "No se encontraron pacientes con los datos proporcionados."}, status=404)

        # Obtener todas las citas de los pacientes encontrados
        citas = Cita.objects.filter(paciente__in=pacientes).order_by('-fecha', '-hora')

        # Si no hay citas asociadas
        if not citas.exists():
            return Response({"error": "No se encontraron citas para los pacientes proporcionados."}, status=404)

        # Formatear la respuesta con los detalles de las citas
        data = []
        for cita in citas:
            diagnostico_detalle = None
            recetas_detalle = []

            if cita.estado == 'finalizada':
                ficha_medica = getattr(cita, 'ficha_medica', None)
                if ficha_medica and ficha_medica.diagnostico:
                    diagnostico = ficha_medica.diagnostico
                    diagnostico_detalle = {
                        "descripcion": diagnostico.descripcion,
                        "es_covid": diagnostico.es_covid,
                        "enfermedad": diagnostico.enfermedad.nombre if diagnostico.enfermedad else None,
                        "triaje": diagnostico.categoria_triaje
                    }

                    # Obtener todas las recetas asociadas al diagnóstico
                    recetas = diagnostico.recetas.all()
                    recetas_detalle = [
                        {
                            "nombre_medicamento": receta.nombre_medicamento,
                            "dosis": receta.dosis,
                            "duracion": receta.duracion,
                            "prescripcion": receta.prescripcion,
                        }
                        for receta in recetas
                    ]

            # Agregar los datos de la cita a la respuesta
            data.append({
                'id': cita.id,
                'fecha': cita.fecha.strftime('%d-%m-%Y'),
                'hora': cita.hora.strftime('%H:%M'),
                'estado': cita.estado,
                'especialidad': cita.especialidad.nombre,
                'medico': f"{cita.medico.user.first_name} {cita.medico.user.last_name}",
                'paciente': f"{cita.paciente.user.first_name} {cita.paciente.user.last_name}",  # Nombres del paciente
                'direccion': cita.direccion,
                'calificacion': cita.calificacion,
                'diagnostico': diagnostico_detalle,  # Solo para finalizadas
                'recetas': recetas_detalle,    
                # Lista de medicamentos
            })

        return Response(data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
