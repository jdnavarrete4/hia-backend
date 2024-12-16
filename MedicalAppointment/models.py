from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User


class Paciente(models.Model):
    
    ROL_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('administrador', 'Administrador'),
    ]
      
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Paciente')
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación con el modelo User
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    numero_cedula = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    contrasena = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.contrasena = make_password(self.contrasena)
        else:
            # Verifica si la contraseña ha cambiado
            original = Paciente.objects.get(pk=self.pk)
            if original.contrasena != self.contrasena:
                self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='medicos')
    correo_electronico = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    contrasena = models.CharField(max_length=100)
    rol = models.CharField(max_length=50, default='medico')
    descripcion = models.TextField(blank=True, null=True)
    foto = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.especialidad.nombre})"
    

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

class Cita(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField(default="09:00")  # Campo obligatorio nuevamente
    estado = models.CharField(max_length=50, default="Reservada")
    direccion = models.CharField(max_length=255)


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

class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Canton(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='cantones')

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"
    
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