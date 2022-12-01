from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone, dateformat
# Create your models here.


CHAR_LENGTH = 255


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        """Create user by email, name, password"""
        if not email:
            raise ValueError('User must have an email!')
        user = self.model(email=self.normalize_email(
            email), name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, name, password):
        """Create superuser by email, name, password"""
        user = self.create_user(email=email, name=name, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model"""
    USERNAME_FIELD = 'email'
    email = models.EmailField(max_length=CHAR_LENGTH, unique=True)
    name = models.CharField(max_length=CHAR_LENGTH)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    User_Type = (
        ('doctor', 'doctor'),
        ('careTaker', 'careTaker'),
    )
    user_type = models.CharField(max_length=40,
                                 choices=User_Type,
                                 default='careTaker'
                                 )
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    def __str__(self):
        return self.email

    def __repr__(self):
        return f"{self.email!r}, {self.is_staff!r}, {self.is_active!r}, "


class Patient(models.Model):
    NRIC = models.CharField(max_length=20)
    name = models.CharField(max_length=40)

    # doctor = models.ForeignKey(
    #     User, related_name="doc", on_delete=models.CASCADE)
    # careTaker = models.ForeignKey(
    #     User, related_name="care", on_delete=models.CASCADE, null=True, blank=True)


class DoctorToPatient(models.Model):
    Patient = models.ForeignKey(
        Patient, related_name="patient_doc", on_delete=models.CASCADE)
    Doctor = models.ForeignKey(
        User, related_name="doc", on_delete=models.CASCADE)


class CaretakerToPatient(models.Model):
    Patient = models.ForeignKey(
        Patient, related_name="patient_care", on_delete=models.CASCADE)
    Caretaker = models.ForeignKey(
        User, related_name="care", on_delete=models.CASCADE)


class MedicalDetails(models.Model):
    Patient = models.ForeignKey(
        Patient, related_name="patient_dets", on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, null=True, blank=True)
    bloodPressure = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    heartRate = models.IntegerField(null=True, blank=True)
    MedicalCondition = models.CharField(max_length=200, default="")
    Medication = models.CharField(max_length=200, default="")
    allergies = models.CharField(max_length=200, default="")


class Task(models.Model):
    Patient = models.ForeignKey(
        Patient, related_name="patient_task", on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    # whether task 1 or 2 or 3 for that date, shld be auto filled when create task
    details = models.CharField(max_length=120, blank=True, null=True)
    editBy = models.CharField(max_length=60, blank=True, null=True)
    editDate = models.DateField(default=timezone.now)
    completedFlag = models.BooleanField(default=False)


class Comments(models.Model):
    task = models.ForeignKey(
        Task, related_name="comment_task", on_delete=models.CASCADE)
    comment = models.CharField(max_length=160, blank=True, null=True)
    editBy = models.CharField(max_length=60, blank=True, null=True)
    editDate = models.DateField(default=timezone.now)
    time = models.TimeField()
