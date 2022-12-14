# Generated by Django 3.2.13 on 2022-10-10 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foolertonApp', '0002_auto_20220915_1444'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='number',
        ),
        migrations.AddField(
            model_name='comments',
            name='time',
            field=models.TimeField(default='12:12 am'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicaldetails',
            name='MedicalCondition',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='medicaldetails',
            name='Medication',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='medicaldetails',
            name='age',
            field=models.IntegerField(default=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='medicaldetails',
            name='allergies',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='medicaldetails',
            name='heartRate',
            field=models.IntegerField(default=101),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='completedFlag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='time',
            field=models.TimeField(default='12:12 am'),
            preserve_default=False,
        ),
    ]
