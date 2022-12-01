from django.contrib import admin

# Register your models here.
from . import models

myModels = [models.Patient, models.CaretakerToPatient, models.DoctorToPatient,
            models.Task, models.MedicalDetails, models.Comments, models.User]
admin.site.register(myModels)
