from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils.timezone import now


class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Canton(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='cantones')

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"
    
class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    numero_cedula = models.CharField(max_length=10)
    fecha_nacimiento = models.DateField()
    direccion = models.TextField(blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE)
    genero = models.CharField(max_length=20, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Otro', 'Otro')])

    
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=99)  # Relación con User
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE, related_name='medicos')
    telefono = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.especialidad.nombre})"

    

class Administrador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    contrasena = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.pk:  # Si el objeto no se ha guardado aún en la base de datos
            self.contrasena = make_password(self.contrasena)
        else:
            # Verifica si la contraseña ha cambiado
            original = Administrador.objects.get(pk=self.pk)
            if original.contrasena != self.contrasena:
                self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# models.py

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="citas")
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="citas")
    fecha = models.DateField()
    hora = models.TimeField(default="09:00")
    estado = models.CharField(
        max_length=50,
        choices=[
            ('reservada', 'Reservada'),
            ('cancelada', 'Cancelada'),
            ('finalizada', 'Finalizada'),
        ],
        default='reservada'
    )
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    calificacion = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Calificación de la cita (1-5, solo para citas finalizadas)."
    )

    class Meta:
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"Cita con {self.medico.user.first_name} para {self.paciente.user.first_name}"



class HistorialMedico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.fecha} - {self.paciente} - {self.medico}"

class Notificacion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha = models.DateTimeField()
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fecha} - {self.paciente} - {'Leída' if self.leida else 'No Leída'}"


    
class Horario(models.Model):
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='horarios')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios', null=True, blank=True)
    dia_semana = models.CharField(
        max_length=15,
        choices=[
            ('lunes', 'Lunes'),
            ('martes', 'Martes'),
            ('miercoles', 'Miércoles'),
            ('jueves', 'Jueves'),
            ('viernes', 'Viernes'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo'),
        ]
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        medico_info = f" - {self.medico.nombre}" if self.medico else ""
        return f"{self.especialidad.nombre} - {self.dia_semana} ({self.hora_inicio} - {self.hora_fin}){medico_info}"
    
class Diagnostico(models.Model):
    descripcion = models.TextField()
    es_covid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    medico = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con User
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    enfermedad = models.ForeignKey('Enfermedad', on_delete=models.CASCADE, null=True, blank=True)  # Relación con Enfermedad


    def __str__(self):
        return f"Diagnóstico de {self.paciente} por {self.medico}"


class Receta(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE, related_name="recetas")
    nombre_medicamento = models.CharField(max_length=255, blank=True, null=True, default="")
    dosis = models.CharField(max_length=255, blank=True, null=True, default="No especificada")
    duracion = models.CharField(max_length=255, blank=True, null=True, default="No especificada")
    prescripcion = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True)

class FichaMedica(models.Model):
    cita = models.OneToOneField('Cita', on_delete=models.CASCADE, related_name='ficha_medica')
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE, related_name='fichas')
    receta = models.ForeignKey('Receta', on_delete=models.CASCADE)  # Relación con Receta
    fecha_creacion = models.DateTimeField(default=now)

    def __str__(self):
        return f"Ficha Médica para Cita {self.cita.id}"
    
class Enfermedad(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre