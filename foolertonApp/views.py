from xml.etree.ElementTree import Comment
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule, ClockedSchedule
import datetime
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from urllib3 import HTTPResponse
import json
from .models import User, Task
from .models import *
from django.core.mail import send_mail
import random


# Create your views here.


def test(request):

    return render(request, 'base.html')


def createUser(request):

    if request.method == "GET":
        return render(request, 'register_page.html')

    if request.method == "POST":
        if(User.objects.filter(email=request.POST['email'])):
            return render(request, 'register_page.html', {'message': 'Email is already in use'})
        if request.POST['password'] != request.POST['repassword']:
            return render(request, 'register_page.html', {'message': 'Passwords do not match'})

        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        userType = 'careTaker'
        use = User.objects.create_user(
            email, name, password)
        use.user_type = userType
        use.save()
        # if(userType == 'careTaker'):
        #     nric = request.POST['nric']
        #     care = CaretakerToPatient.objects.create(
        #         Caretaker=use, Patient=Patient.objects.get(NRIC=nric))
        #     care.save()
        content = {'Success': "created for " + use.name}
        return render(request, 'register_page.html', content)


def createtasks(request, name, date):
    if request.method == "GET":
        user = request.user
        if(user.user_type == 'doctor'):
            patients = DoctorToPatient.objects.filter(Doctor=user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            tasklist = Task.objects.all().filter(
                Patient__pk=name, date=date).order_by('time')
            comment = []
            task_complete = []
            for i in tasklist:
                comments = i.comment_task.all()
                comment.append({"tasked": i, "comment": comments})
                task_complete.append(i.completedFlag)
            context = {
                'comments': comment,
                'dates': date,
                'people': ppl,
                'current': name,
                'name': request.user.name,
            }
            # For js convenience
            context["task_completedFlag"] = json.dumps(task_complete)
            return render(request, 'tasks_page_main.html', context)
        if(user.user_type == 'careTaker'):
            patients = CaretakerToPatient.objects.filter(Caretaker=user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            tasklist = Task.objects.all().filter(
                Patient__pk=name, date=date).order_by('time')
            comment = []
            task_complete = []
            for i in tasklist:
                comments = i.comment_task.all()
                comment.append({"tasked": i, "comment": comments})
                task_complete.append(i.completedFlag)
            context = {
                'comments': comment,
                'dates': date,
                'people': ppl,
                'current': name,
                'name': request.user.name
            }
            context["task_completedFlag"] = json.dumps(task_complete)
            return render(request, 'tasks_page_main_care.html', context)


def createdtasks(request):
    if request.method == "POST":
        if request.POST.get("form_type") == 'addtask':

            id = request.POST.get('person')
            Patiented = Patient.objects.filter(
                pk=id).first()  # testing
            date = request.POST.get('datecomplete')
            time = request.POST.get('timecomplete')
            details = request.POST.get('taskdesc')
            editBy = request.user.name

            newTask = Task(date=date, Patient=Patiented,
                           time=time, details=details, editBy=editBy)
            newTask.save()
            dat = datetime.datetime.combine(datetime.datetime.strptime(
                date, '%Y-%m-%d').date(), datetime.datetime.strptime(time, '%H:%M').time())
            dat = dat - datetime.timedelta(hours=1)
            schedule, created = ClockedSchedule.objects.get_or_create(
                clocked_time=dat)
            task = PeriodicTask.objects.create(
                clocked=schedule, name=str(datetime.datetime.now())+newTask.date+newTask.time+str(Patiented.pk), task='foolertonApp.tasks.autoemail', one_off=True)
            whr = '/createtasks/'+str(Patiented.pk)+'/'+date
            return redirect(whr)
    # just load this first if it doesnt work
    return render(request, 'loginpg.html')


def createcomments(request):
    if request.method == "POST":
        Tasked = Task.objects.filter(pk=request.POST.get('task')).first()
        comment = request.POST.get('comment_desc')
        date = request.POST.get('date')
        print(date, "adsdas")
        com = Comments.objects.create(
            task=Tasked, comment=comment, editBy=request.user.name, editDate=datetime.datetime.now(), time=datetime.datetime.now())
        com.save()
        name = request.POST.get('name')
        whr = '/createtasks/'+name+'/'+date
        return redirect(whr)


def updatetasks(request):
    if request.method == "POST":
        if request.POST.get("form_type") == 'updatetask':

            name = request.POST.get('name')
            Patiented = Patient.objects.filter(
                name=name).first()  # testing
            date = request.POST.get('datecomplete')
            time = request.POST.get('timecomplete')
            details = request.POST.get('taskdesc')
            editBy = request.user.name
            # Patient_id = 1
            newTask = Task.objects.filter(pk=request.POST.get('task')).first()
            newTask.date = date
            newTask.time = time
            newTask.details = details
            newTask.editBy = editBy
            newTask.save()
            whr = '/createtasks/'+name+'/'+date
            return redirect(whr)
    # just load this first if it doesnt work
    return render(request, 'loginpg.html')


def deleteTask(request):
    if request.method == "DELETE":
        data = json.loads(request.body.decode("utf-8"))
        id = int(data["task_id"])
        task = Task.objects.filter(id=id).first()
        if(task):
            task.delete()
            res = HttpResponse(f"Success, Task {id} is deleted")
            res.status_code = 200
            return res
        else:
            res = HttpResponse(f"Error Task {id} Not Found")
            res.status_code = 400
            return res


def MarkTask(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        id = int(data["task_id"])
        task = Task.objects.filter(id=id).first()
        if(task):
            task.completedFlag = not task.completedFlag
            task.save()
            if task.completedFlag:
                res = HttpResponse(f"Success, Task {id} set as completed")
            else:
                res = HttpResponse(f"Success, Task {id} set as uncompleted")
            res.status_code = 200
            return res
        else:
            res = HttpResponse("Failure, cannot find task")
            res.status_code = 400
            return res


def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'doctor':
                patients = DoctorToPatient.objects.filter(Doctor=user).first()

                if patients == None:
                    patients = "-1"
                else:
                    patients = patients.Patient.pk
                whr = '/createtasks/'+str(patients) + \
                    '/'+str(datetime.datetime.now().date())
                return redirect(whr)
            if user.user_type == 'careTaker':
                patients = CaretakerToPatient.objects.filter(
                    Caretaker=user).first()

                if patients == None:
                    patients = "-1"
                else:
                    patients = patients.Patient.pk
                whr = '/createtasks/'+str(patients)+'/' + \
                    str(datetime.datetime.now().date())
                return redirect(whr)
        else:
            message = "Unsuccessful login! Please enter the right email and password!"
            return render(request, 'login_page.html', {'message': message})
    if request.method == "GET":
        return render(request, 'login_page.html')


def view_tasks(request):
    if request.method == "GET":
        query_tasks = Task.objects.filter(
            Patient=request.GET['patient_id'],
            date=request.GET['date']
        ).order_by('number')
        if query_tasks is not None:
            tasks_comments_dict = {}
            for task in query_tasks:
                # cant seem to fetch comments due to conversion error?
                query_comment = Comments.objects.filter(task_id=task.id)
                if query_comment is not None:
                    comments_dict = {
                        comment.id: comment for comment in query_comment}
                    tasks_comments_dict[task.number] = (
                        task, comments_dict)
                else:
                    tasks_comments_dict[task.number] = (task, None)
            print(tasks_comments_dict)
            return render(request, 'testpage.html', {'task_query': tasks_comments_dict})
    return render(request, 'testpage.html', {'task_query': None})


def mark_task_as_completed(request):
    if request.method == "POST":
        task = Task.objects.filter(id=request.POST['task_id'])
        print(task)
        task.completedFlag = True
        try:
            task.save()
        except Task.DoesNotExist:
            print("Task does not exist")
            return
        except Exception:
            print("error in saving task")
            print(Exception)
            return
        print("Task marked as completed")
        return render(request, 'testpage.html')
    elif request.method == "GET":
        return render(request, 'testpage.html')


def upload_medical(request):
    if request.method == "POST":
        if request.user.user_type == 'doctor':
            patient_id = request.POST.get('id')
            patient = Patient.objects.filter(pk=patient_id).first()
            date = datetime.datetime.now().date()
            blood_pressure = request.POST['blood']
            height = request.POST['height']
            weight = request.POST['weight']
            age = request.POST['age']
            heart = request.POST['heart']
            medical = request.POST['medical']
            medication = request.POST['medication']
            allergy = request.POST['allergies']
            patient_medical, fact = MedicalDetails.objects.get_or_create(
                Patient=patient)

            patient_medical.bloodPressure = blood_pressure
            patient_medical.height = height
            patient_medical.weight = weight
            patient_medical.date = date
            patient_medical.age = age
            patient_medical.heartRate = heart
            patient_medical.MedicalCondition = medical
            patient_medical.Medication = medication
            patient_medical.allergies = allergy
            patient_medical.save()
            whr = 'http://127.0.0.1:8000/healthinfo/' + \
                str(patient_medical.Patient.pk)
            return redirect(whr)
        if request.user.user_type == 'careTaker':
            patient_id = request.POST.get('id')
            date = datetime.datetime.now().date()
            blood_pressure = request.POST['blood']
            heart = request.POST['heart']
            patient_medical = MedicalDetails.objects.get(
                Patient__pk=patient_id)
            patient_medical.bloodPressure = blood_pressure
            patient_medical.date = date
            patient_medical.heartRate = heart
            patient_medical.save()
            whr = 'http://127.0.0.1:8000/healthinfo/' + \
                str(patient_medical.Patient.pk)
            return redirect(whr)


def healthinfo(request, name):
    if request.method == "GET":
        if(request.user.user_type == 'doctor'):
            patients = DoctorToPatient.objects.filter(Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            patient = Patient.objects.filter(pk=name).first()
            details = MedicalDetails.objects.filter(Patient=patient).first()

            return render(request, 'health_info.html', {'pat': patient, 'det': details, 'current': name, 'people': ppl, 'name': request.user.name, 'date': str(datetime.datetime.now().date())})
        if(request.user.user_type == 'careTaker'):
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            patient = Patient.objects.filter(pk=name).first()
            details = MedicalDetails.objects.filter(Patient=patient).first()

            return render(request, 'health_info_care.html', {'pat': patient, 'det': details, 'current': name, 'people': ppl, 'name': request.user.name, 'date': str(datetime.datetime.now().date())})


def docacc(request):
    if request.method == "GET":
        if(request.user.user_type == 'doctor'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_main.html', {'name': request.user.name, "people": ppl, "current": current, "email": request.user.email, "date": str(datetime.datetime.now().date())})
        if(request.user.user_type == 'careTaker'):
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_main_care.html', {'name': request.user.name, "people": ppl, "current": current, "email": request.user.email, "date": str(datetime.datetime.now().date())})
    if request.method == "POST":
        whr = '/'+request.POST.get('options')
        return redirect(whr)


def logoutacc(request):

    logout(request)
    whr = 'http://127.0.0.1:8000'
    return redirect(whr)


def manage(request):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'manage_patient_profiles.html', {"name": request.user.name, "people": ppl, "date": str(datetime.datetime.now().date()), "current": ppl[0].pk})
    if request.method == "POST":
        user = request.user
        act = request.POST.get('action')
        person = request.POST.get('person')
        if(act == 'addpat'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            return render(request, 'create_patient_profile.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "date": str(datetime.datetime.now().date())})
        if(act == 'removepat'):

            pat = Patient.objects.filter(name=person).first()
            pat.delete()
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            return render(request, 'manage_patient_profiles.html', {"message": "successfully deleted "+person, "people": ppl, "current": ppl[0].pk, "name": request.user.name, "date": str(datetime.datetime.now().date())})
        if(act == 'addcare'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            whr = 'http://127.0.0.1:8000/addcare/'+person
            return redirect(whr)

        if(act == 'removecare'):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            whr = 'http://127.0.0.1:8000/removecare/'+person
            return redirect(whr)


def removecare(request, pat):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        care = CaretakerToPatient.objects.filter(Patient__name=pat)
        caretakers = []
        for i in care:
            caretakers.append(i.Caretaker)

        return render(request, 'remove_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "patient": pat, "caretakers": caretakers})
    if request.method == "POST":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        care = User.objects.filter(pk=request.POST.get('caretaker')).first()
        patient = Patient.objects.filter(name=pat).first()
        dis = CaretakerToPatient.objects.filter(
            Caretaker=care, Patient=patient).first()
        dis.delete()
        carer = CaretakerToPatient.objects.filter(Patient__name=pat)
        caretakers = []
        for i in carer:
            caretakers.append(i.Caretaker)
        return render(request, 'remove_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "patient": pat, "caretakers": caretakers, "message": "Successfully removed "+care.name+" from "+pat})


def addcare(request, pat):
    if request.method == "GET":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)

        return render(request, 'add_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "patient": pat, "date": str(datetime.datetime.now().date())})
    if request.method == "POST":
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        email = request.POST.get('email')
        care = User.objects.filter(email=email).first()
        if(not care):
            return render(request, 'add_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "message": "Email does not exist", "patient": pat, "date": str(datetime.datetime.now().date())})
        patiented = Patient.objects.filter(name=pat).first()
        if(CaretakerToPatient.objects.filter(
                Caretaker=care, Patient=patiented)):
            return render(request, 'add_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "message": patiented.name+" already linked to "+care.name, "patient": pat, "date": str(datetime.datetime.now().date())})
        connect = CaretakerToPatient.objects.create(
            Caretaker=care, Patient=patiented)
        return render(request, 'add_caretaker.html', {"people": ppl, "name": request.user.name, "current": ppl[0].pk, "message": "Successfully added "+care.name+" to "+pat, "patient": pat, "date": str(datetime.datetime.now().date())})


def createpat(request):
    if request.method == "POST":
        name = request.POST.get('name')
        nric = request.POST.get('nric')
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        if(Patient.objects.filter(NRIC=nric)):
            return render(request, 'create_patient_profile.html', {"name": request.user.name, "current": ppl[0].pk, "people": ppl, "message": "Unsuccessful: NRIC already exists", "date": str(datetime.datetime.now().date())})
        pat = Patient.objects.create(NRIC=nric, name=name)
        connect = DoctorToPatient.objects.create(
            Patient=pat, Doctor=request.user)
        patients = DoctorToPatient.objects.filter(
            Doctor=request.user)
        ppl = []
        for patient in patients:
            ppl.append(patient.Patient)
        return render(request, 'create_patient_profile.html', {"name": request.user.name, "current": ppl[0].pk, "people": ppl, "message": "successfully created "+name, "date": str(datetime.datetime.now().date())})


def update(request):
    if request.method == "GET":
        if(request.user.user_type == "doctor"):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_update.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date())})
        if(request.user.user_type == "careTaker"):
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_update.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date())})
    if request.method == 'POST':
        if(request.user.user_type == "doctor"):
            user = request.user
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            print(request.POST.get('email'), 'try')
            user.email = request.POST.get('email')
            user.name = request.POST.get('name')
            user.save()
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_update.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date())})
        if(request.user.user_type == "careTaker"):
            user = request.user
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            print(request.POST.get('email'), 'try')
            user.email = request.POST.get('email')
            user.name = request.POST.get('name')
            user.save()
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_update.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date())})


def change(request):
    if request.method == "GET":
        if(request.user.user_type == "doctor"):
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date())})
        if(request.user.user_type == "careTaker"):
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date())})
    if request.method == 'POST':
        if request.user.user_type == "doctor":
            user = request.user
            patients = DoctorToPatient.objects.filter(
                Doctor=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            print(user.password, user.email)
            new_user = authenticate(request, email=user.email,
                                    password=request.POST.get('old_password'))
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            if(request.POST.get('new_password') != request.POST.get('check') or (not new_user)):
                return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, 'wrongpassword': "please enter the right password or new passwords do not match", "current": current, "date": str(datetime.datetime.now().date())})
            new_user.set_password(request.POST.get('new_password'))
            new_user.save()
            login(request, new_user)
            return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date()), 'wrongpassword': "Successfully Changed"})
        if request.user.user_type == "careTaker":
            user = request.user
            patients = CaretakerToPatient.objects.filter(
                Caretaker=request.user)
            ppl = []
            for patient in patients:
                ppl.append(patient.Patient)
            print(user.password, user.email)
            new_user = authenticate(request, email=user.email,
                                    password=request.POST.get('old_password'))
            current = ''
            if(ppl != []):
                current = ppl[0].pk
            if(request.POST.get('new_password') != request.POST.get('check') or (not new_user)):
                return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, 'wrongpassword': "please enter the right password or new passwords do not match", "current": current, "date": str(datetime.datetime.now().date())})
            new_user.set_password(request.POST.get('new_password'))
            new_user.save()
            login(request, new_user)
            return render(request, 'doc_account_changePW.html', {'people': ppl, 'name': request.user.name, 'email': request.user.email, "current": current, "date": str(datetime.datetime.now().date()), 'wrongpassword': "Successfully Changed"})


# Test API endpoint/template

def testHTTPEndPoint(request):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"}
    if request.method == "GET":
        paramLst = request.GET
        # paramLst = request.POST
        # paramLst = request.GET["item1"]
        res = HttpResponse([paramLst, "GET request received!"])
        res.status_code = 200
        return res
    if request.method == "POST":
        paramLst = json.loads(request.body.decode("utf-8"))
        print(paramLst)
        res = HttpResponse([paramLst, "GET request received!"])
        res.status_code = 200
        return res


# Test API endpoint/template

def testHTTPEndPoint(request):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"}
    if request.method == "GET":
        paramLst = request.GET
        # paramLst = request.POST
        # paramLst = request.GET["item1"]
        res = HttpResponse([paramLst, "GET request received!"])
        res.status_code = 200
        return res
    if request.method == "POST":
        paramLst = json.loads(request.body.decode("utf-8"))
        print(paramLst)
        res = HttpResponse([paramLst, "POST request received!"])
        res.status_code = 200
        return res


def notification(request):
    if request.method == "GET":
        forwho = Task.objects.filter(
            date=datetime.datetime.now().date(), time__gte=(datetime.datetime.now() + datetime.timedelta(0, 59, 0)).time(), time__lte=(datetime.datetime.now()+datetime.timedelta(1, 1, 0)).time())
        for i in forwho:
            subject = "task for " + i.Patient.name + " in 1 hour"
            message = i.details
            email = "test",
            people = CaretakerToPatient.filter(Patient=i.Patient)
            peeps = []
            for ppl in people:
                peeps.append(ppl.Caretaker.email)
            send_mail(
                subject,
                message,
                email,
                ['lewxunyi@gmail.com'],
            )
        # send_mail(
        #     "hi",
        #     "message",
        #     "email",
        #     ["lewxunyi@gmail.com"],
        # )

        res = HttpResponse(f"mail sent")
        return res


def taskcre(request):
    if request.method == "GET":
        john = Patient.objects.get(name="John")
        mary = Patient.objects.get(name="Mary")
        doc = User.objects.get(name="doc")
        for i in range(0, 31):
            time = "11"+":30"
            # Task.objects.create(Patient=john, date=datetime.datetime(2022, 10, 1+i), time=datetime.datetime.strptime(
            #     time, '%H:%M').time(), details="take blood pressure", editBy=doc, editDate=datetime.datetime.now())
            Task.objects.create(Patient=mary, date=datetime.datetime(2022, 10, 1+i), time=datetime.datetime.strptime(
                time, '%H:%M').time(), details="eat medication", editBy=doc, editDate=datetime.datetime.now())
        return HttpResponse(f"good")
