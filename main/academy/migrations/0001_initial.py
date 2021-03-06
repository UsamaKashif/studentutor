# Generated by Django 3.0.4 on 2020-08-31 17:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Academy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('textArea', models.CharField(default='', max_length=300, null=True)),
                ('username', models.CharField(default='username', max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('city', models.CharField(max_length=100)),
                ('total_ads', models.IntegerField(default=0)),
                ('ads_deleted', models.IntegerField(default=0)),
                ('phone', models.CharField(max_length=11)),
                ('profile_complete', models.BooleanField(default=False)),
                ('invitations_sent', models.IntegerField(default=0)),
                ('invitations_sent_accepted', models.IntegerField(default=0)),
                ('invitations_sent_rejected', models.IntegerField(default=0)),
                ('invitations_recieved', models.IntegerField(default=0)),
                ('invitations_recieved_accepted', models.IntegerField(default=0)),
                ('invitations_recieved_rejected', models.IntegerField(default=0)),
                ('ad_post_count', models.IntegerField(default=0)),
                ('user_image', models.ImageField(default='user_profile_default.jpg', upload_to='profile_pics_stds')),
                ('academy', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
