# Generated by Django 3.0.4 on 2020-04-14 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_auto_20200414_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='textArea',
            field=models.TextField(default='', max_length=300, null=True),
        ),
        migrations.DeleteModel(
            name='AboutStudent',
        ),
    ]
