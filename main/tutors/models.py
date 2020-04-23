from django.db import models
from django.contrib.auth.models import User

from PIL import Image
# Create your models here.



class Tutor(models.Model):
    username = models.CharField(max_length=200, null=True, default="")
    

    tutor = models.OneToOneField(User, null=True, on_delete=models.CASCADE) 
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    age = models.IntegerField()
    gender=models.CharField(max_length=6)
    phone=models.CharField(max_length=11)
    email = models.EmailField()
    city = models.CharField(max_length=100, null=True)
    cnic = models.CharField(max_length=13, null=True)
    verified = models.BooleanField(default=False, null=True)
    verification_sent = models.BooleanField(default=False)
    total_ads = models.IntegerField(default=0)
    ads_deleted = models.IntegerField(default=0)


    invitations_sent = models.IntegerField(default=0)    #done
    invitations_sent_accepted = models.IntegerField(default=0)  #done
    invitations_sent_rejected = models.IntegerField(default=0)  #done

    invitations_recieved = models.IntegerField(default=0)   #done 
    invitations_recieved_accepted = models.IntegerField(default=0) #done
    invitations_recieved_rejected = models.IntegerField(default=0) #done

    tagline = models.CharField(max_length=50)
    about = models.CharField(max_length=300)

    ad_post_count = models.IntegerField(default=0)

    about_complete = models.BooleanField(default=False)
    qual_complete = models.BooleanField(default=False)

    user_image = models.ImageField(default="user_profile_default.jpg", upload_to="profile_pics_tutors")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.user_image.path)

        if img.height > 250 or img.width > 250:
            outputSize = (250, 250)

            img.thumbnail(outputSize)
            img.save(self.user_image.path)


class PostAnAd(models.Model):
    tutorUser = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True)
    # tutorUser = models.CharField(max_length=300, null=True, blank=True)

    views = models.IntegerField(default=0)

    subject = models.CharField(max_length=300)
    tuition_level = models.CharField(max_length=300)


    can_travel = models.CharField(max_length=100, null=True)

    address = models.CharField(max_length=300)

    estimated_fees = models.IntegerField()


    def __str__(self):
        return f'{self.subject} : {self.tuition_level} : {self.tutorUser}'

from students.models import Student

class Invitaions(models.Model):
    inivitaion_by_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True) # username of student
    tutor_ad = models.ForeignKey(PostAnAd, on_delete=models.CASCADE, null=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    invitation_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'Invitaion By {self.inivitaion_by_student}'

class AboutAndQualifications (models.Model):
    tutor = models.OneToOneField(Tutor, on_delete=models.CASCADE)

    highest_qual = models.CharField(max_length=100)
    highest_qual_inst = models.CharField(max_length=100)

    secondary_qaul = models.CharField(max_length=100)
    secondary_qaul_inst = models.CharField(max_length=100)

    def __str__(self):
        return self.tutor.username


class Verify(models.Model):
    tutor = models.OneToOneField(Tutor, on_delete=models.CASCADE)

    cnic_front = models.ImageField()
    cnic_back = models.ImageField()
    highist_qual = models.ImageField()


    def __str__(self):
        return self.tutor.username