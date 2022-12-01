from __future__ import absolute_import, unicode_literals

from celery import shared_task
import requests
from .models import Task, CaretakerToPatient
import datetime
from django.core.mail import send_mail


@shared_task
def autoemail():

    forwho = Task.objects.filter(
        date=datetime.datetime.now().date(), time__gte=(datetime.datetime.now() + datetime.timedelta(minutes=59)).time(), time__lte=(datetime.datetime.now()+datetime.timedelta(hours=1, minutes=1)).time())
    print(forwho)
    print("hi ", (datetime.datetime.now() + datetime.timedelta(minutes=59)).time(),
          ' ', (datetime.datetime.now()+datetime.timedelta(hours=1, minutes=1)).time(), ' ', datetime.datetime.now().date())
    for i in forwho:
        subject = "Task for " + i.Patient.name + " in 1 hour"
        message = i.details
        email = "test"
        people = CaretakerToPatient.objects.filter(Patient=i.Patient)
        peeps = []
        for ppl in people:
            peeps.append(ppl.Caretaker.email)
        send_mail(
            subject,
            message,
            email,
            peeps,
        )
    # send_mail(
    #     "hi",
    #     "message",
    #     "email",
    #     ["lewxunyi@gmail.com"],
    # )

    return


@shared_task
def debug():

    print("test")
    return
