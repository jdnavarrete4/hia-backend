from rest_framework import serializers
from .models import Paciente, Medico, Administrador, Cita, HistorialMedico, Notificacion, Receta, Diagnostico



class PacienteSerializer(serializers.ModelSerializer):
    # Campos relacionados del modelo User
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    provincia_nombre = serializers.CharField(source='provincia.nombre', read_only=True)
    canton_nombre = serializers.CharField(source='canton.nombre', read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'telefono', 'fecha_nacimiento', 'direccion',
            'provincia', 'provincia_nombre', 'canton', 'canton_nombre', 'genero',
            'first_name', 'last_name', 'email','tipo_identificacion',
            'numero_identificacion','pais'
        ]



class RegistroPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        exclude = ['direccion']  # Excluir el campo direccion
      

class MedicoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='user.first_name', read_only=True)
    apellido = serializers.CharField(source='user.last_name', read_only=True)
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)


    class Meta:
        model = Medico
        fields = [
            'id',
            'telefono',
            'descripcion',
            'foto',
            'especialidad',
            'especialidad_nombre',
            'user',
            'nombre',
            'apellido',
        ]

class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = '__all__'





# serializers.py
class CitaSerializer(serializers.ModelSerializer):
    # Esto anida todo el JSON del paciente
    paciente = PacienteSerializer(read_only=True)
    medico_id = serializers.IntegerField(source="medico.id", read_only=True)  # Agrega este campo

    # Esto mantiene el nombre completo del médico, tal y como lo hacías antes
    medico_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Cita
        fields = [
            'id', 'fecha', 'hora', 'estado', 'direccion', 'descripcion', 'motivo',
            'paciente',       # <--- Devuelve los datos completos del paciente
            'medico_nombre',
            'especialidad', 
            'medico_id'
        ]

    def get_medico_nombre(self, obj):
        return (
            f"{obj.medico.user.first_name} {obj.medico.user.last_name}"
            if obj.medico
            else "No asignado"
        )




class HistorialMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialMedico
        fields = '__all__'

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'
        
class LoginSerializer(serializers.Serializer):
    correo_electronico = serializers.EmailField()
    contrasena = serializers.CharField()


class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ['id', 'diagnostico', 'nombre_medicamento', 'dosis', 'duracion', 'prescripcion', 'created_at', 'notas']

class DiagnosticoSerializer(serializers.ModelSerializer):
    recetas = RecetaSerializer(many=True)

    class Meta:
        model = Diagnostico
        fields = '__all__'

    def create(self, validated_data):
        recetas_data = validated_data.pop('recetas')
        diagnostico = Diagnostico.objects.create(**validated_data)
        for receta_data in recetas_data:
            Receta.objects.create(diagnostico=diagnostico, **receta_data)
        return diagnostico