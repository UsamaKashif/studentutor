from django.db import models
from django.contrib.auth.models import User

from django.urls import reverse

from PIL import Image
# Create your models here.

class Student(models.Model):

    textArea = models.CharField(max_length=300, null=True, default="")


    student = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100, default="username")
    age = models.IntegerField(default=0)
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, default="first name")
    last_name = models.CharField(max_length=100, default="last name")
    total_ads = models.IntegerField(default=0)
    ads_deleted = models.IntegerField(default=0)
    phone=models.CharField(max_length=11)

    profile_complete = models.BooleanField(default=False)

    invitations_sent = models.IntegerField(default=0)  #done
    invitations_sent_accepted = models.IntegerField(default=0) #done
    invitations_sent_rejected = models.IntegerField(default=0) #done

    invitations_recieved = models.IntegerField(default=0)  #done
    invitations_recieved_accepted = models.IntegerField(default=0)  #done
    invitations_recieved_rejected = models.IntegerField(default=0)  #done


    ad_post_count = models.IntegerField(default=0)

    user_image = models.ImageField(default="user_profile_default.jpg", upload_to="profile_pics_stds")


    def __str__(self):
        return f'{self.username} : {self.id}'

    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.user_image.path)

        if img.height > 250 or img.width > 250:
            outputSize = (250, 250)

            img.thumbnail(outputSize)
            img.save(self.user_image.path)



class PostAnAd(models.Model):
    studentUser = models.ForeignKey(Student, null=True, on_delete=models.CASCADE)
    # studentUser = models.CharField(max_length=300, null=True, blank=True)

    views = models.IntegerField(default=0)
    

    subject = models.CharField(max_length=100, default="English")
    tuition_level = models.CharField(max_length=100, default="O Level")


    tuition_type = models.CharField(max_length=100, null=True)

    address = models.CharField(max_length=300)

    hours_per_day = models.IntegerField()
    days_per_week = models.IntegerField()

    estimated_fees = models.IntegerField()


    def __str__(self):
        return f'{self.subject} : {self.tuition_level} : {self.studentUser.username} : {self.studentUser.id}'

from tutors.models import Tutor

class TutorInvitaions(models.Model):
    inivitaion_by_tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True) 
    student_ad = models.ForeignKey(PostAnAd, on_delete=models.CASCADE, null=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    invitation_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'Invitaion By {self.inivitaion_by_tutor.username} : {self.inivitaion_by_tutor.id}'