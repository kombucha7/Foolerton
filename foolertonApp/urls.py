from django.urls import path, include

from . import views

app_name = 'foolerton'

urlpatterns = [
    path('', views.login_user, name='login'),
    path('logout', views.logoutacc, name='logout'),
    path('createuser', views.createUser, name='createuser'),
    path('createtasks', views.createtasks, name='createtasks'),
    path('createtasks/<name>/<date>', views.createtasks, name='createtasks'),
    path('createdtasks', views.createdtasks, name='createdtasks'),
    path('updatetasks', views.updatetasks, name='updatetasks'),
    path('delete', views.deleteTask, name="deleteTask"),
    path('mark', views.MarkTask, name="MarkTask"),
    path('tasks/', views.view_tasks, name='tasks'),
    path('tasks', views.view_tasks, name='tasks'),
    path('completedtasks', views.mark_task_as_completed, name='completedtasks'),
    path('uploadMedical', views.upload_medical, name='upload_medical'),
    path('healthinfo', views.healthinfo, name='healthinfo'),
    path('healthinfo/<name>', views.healthinfo, name='healthinfo'),
    path('docacc', views.docacc, name='docacc'),
    path('manage', views.manage, name='manage'),
    path('update', views.update, name='update'),
    path('change', views.change, name='change'),
    path('createpat', views.createpat, name='createpat'),
    path('addcare/<pat>', views.addcare, name='addcare'),
    path('removecare/<pat>', views.removecare, name='removecare'),
    path('createcomments', views.createcomments, name='createcomments'),
    path('testHTTPEndPoint', views.testHTTPEndPoint, name='testHTTPEndPoint'),
    path('email', views.notification, name='notification'),
    path('test', views.taskcre, name='test'),
]
