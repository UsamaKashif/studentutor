# Generated by Django 3.0.4 on 2020-04-14 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_auto_20200414_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='textArea',
            field=models.CharField(default='', max_length=300, null=True),
        ),
    ]
