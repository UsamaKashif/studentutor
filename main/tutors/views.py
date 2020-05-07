from django.shortcuts import render, redirect

from .forms import TutorSignUpform, TutorProfile, PostAnAdForm, QualificationForm, ProfilePicture, AboutForm, VerifyForm
from .models import Tutor, Invitaions, AboutAndQualifications, Verify

from .models import PostAnAd as PostAnAd_tut

from students.models import PostAnAd as PostAnAd_std
from students.models import TutorInvitaions, Student

from django.contrib.auth.models import Group


from students.decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.core.mail import EmailMessage
from django.conf import settings 
from django.template.loader import render_to_string
# Create your views here.



def tutorRegister(request):

    form = TutorSignUpform()

    

    if request.method == "POST":
        form = TutorSignUpform(request.POST)
        
        if form.is_valid():
            tutor = form.save()
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            age = form.cleaned_data.get('age')
            city = form.cleaned_data.get('city')
            firstName = form.cleaned_data.get('first_name')
            lastName = form.cleaned_data.get('last_name')
            gender = form.cleaned_data.get('gender')
            cnic = form.cleaned_data.get('cnic')
            phone = form.cleaned_data.get('phone')

            group = Group.objects.get(name="tutors")
            tutor.groups.add(group)

            Tutor.objects.create(
                tutor = tutor,
                first_name= firstName,
                last_name = lastName,
                age = age,
                city = city,
                gender = gender,
                email = email,
                cnic = cnic,
                username = username,
                phone = phone
            )

            template = render_to_string("home/registerEmail.html", {
                "firstname": firstName,
                "lastname": lastName,
                "register_as" : "tutor"
            })
            registerEmail = EmailMessage(
                'Registration Successful',
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )
            registerEmail.fail_silently = False
            registerEmail.send()

            messages.success(request,'account was created for ' + username)
            return redirect("sign_in")

    context = {
        "form": form,
    }
    return render(request, "tutors/tutor_register.html", context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def tutorDashboard(request):
    tutor = request.user.tutor

    form = TutorProfile(instance=tutor)

    user = Tutor.objects.get(username = request.user.username)

    active_ads = PostAnAd_tut.objects.filter(tutorUser = request.user.tutor).count()

    p_form = ProfilePicture()

    try:
        tutorAbout = AboutAndQualifications.objects.get(tutor__username = request.user.username)
    except:
        tutorAbout = None

    if request.method=="POST":
        form = TutorProfile(request.POST,request.FILES, instance=tutor)
        p_form = ProfilePicture(request.POST, request.FILES)

        if p_form.is_valid():
            image = p_form.cleaned_data["image"]
            profile_image = Tutor.objects.get(username = request.user.username)
            profile_image.user_image = image
            profile_image.save()
            
            return redirect("tutor_dashboard")
        else:
            messages.warning(request, 'Supported File Extensions are .jpg And .png, Max Image Size Is 1MB')
            return redirect("tutor_dashboard")
        if form.is_valid():
            form.save()

    context={
        "form": form,
        "p_form": p_form,
        "totalAds": user.total_ads,
        "adsDel": user.ads_deleted,
        "activeAds": active_ads,
        "invitations_sent": user.invitations_sent,
        "invitations_sent_accepted": user.invitations_sent_accepted,
        "invitations_sent_rejected": user.invitations_sent_rejected,
        "invitations_recieved": user.invitations_recieved,
        "invitations_recieved_accepted": user.invitations_recieved_accepted,
        "invitations_recieved_rejected": user.invitations_recieved_rejected,

        "about": tutorAbout
    }

    return render(request, 'tutors/tutor_dashboard.html', context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def postAnAd(request, pk):
    postForm = PostAnAdForm()
    user = Tutor.objects.get(username = request.user.username)

    tutorAds = PostAnAd_tut.objects.filter(tutorUser__username = request.user.username)
    if request.method == "POST":
        postForm = PostAnAdForm(request.POST)
        if postForm.is_valid():
            subject = postForm.cleaned_data['subject']
            tuition_level = postForm.cleaned_data['tuition_level']
            can_travel = postForm.cleaned_data['can_travel']
            estimated_fees = postForm.cleaned_data['estimated_fees']
            address = postForm.cleaned_data['address']

            adAvailabel = False

            for ad in tutorAds:
                if ad.subject == subject and ad.tuition_level == tuition_level:
                    adAvailabel = True
            
            if adAvailabel  == False:
                PostAnAd_tut.objects.create(
                    tutorUser = user,
                    subject = subject,
                    tuition_level = tuition_level,
                    can_travel = can_travel,
                    estimated_fees = estimated_fees,
                    address = address
                )
                user.total_ads += 1
                user.ad_post_count += 1
                user.save()
                messages.info(request, "Your post is Successfully Created")
                return redirect('tutor_dashboard')
            else:
                messages.info(request, "This AD Already Exists")
                return redirect('tutor_dashboard')
    context = {
        "form":postForm
    }
    return render(request, "tutors/post_ad.html", context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def ads(request):
    ads = PostAnAd_tut.objects.filter(tutorUser=request.user.tutor).order_by("-id")
    try:
        tutorAbout = AboutAndQualifications.objects.get(tutor__username = request.user.username)
    except:
        tutorAbout = None
    
    context = {
        "ads":ads,
        "about": tutorAbout
    }

    return render(request, "tutors/ads.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def adsDelete(request, pk):
    ad = PostAnAd_tut.objects.get(id=pk)
    user = Tutor.objects.get(username=request.user.username)
    if request.method == "POST":
        ad.delete()
        user.ads_deleted += 1
        user.ad_post_count -= 1
        user.save()
        return redirect("ads_tutor")

    context = {
        "ad":ad
    }

    return render(request, 'tutors/delete_ad.html', context)


from students.models import Student

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def invitations(request):
    invites = Invitaions.objects.filter(tutor_ad__tutorUser = request.user.tutor).order_by("-id")
    

    context = {
        "invites":invites
    }

    return render(request, 'tutors/invitations.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def view_your_ad(request, id):
    tutor_ad = Invitaions.objects.get(id = id)
    try:
        students = PostAnAd_std.objects.filter(subject = tutor_ad.tutor_ad.subject)[4]
    except:
        students = PostAnAd_std.objects.filter(subject = tutor_ad.tutor_ad.subject)

    context = {
        "invite":tutor_ad,
        "students": students.exclude(studentUser__username = tutor_ad.inivitaion_by_student.username)
    }
    return render(request,'tutors/view_your_ad.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def confirmInvite(request, id):

    invite = Invitaions.objects.get(id = id)

    tutor = Tutor.objects.get(username = request.user.username)

    std = Student.objects.get(username = invite.inivitaion_by_student.username)

    if request.method == "POST":
        invite.accepted = True
        invite.rejected = False
        invite.save()
        tutor.invitations_recieved_accepted += 1
        tutor.save()

        std.invitations_sent_accepted += 1
        std.save()

        template = render_to_string("home/acceptEmail.html", {
                    "firstname": request.user.tutor.first_name,
                    "lastname": request.user.tutor.last_name,
                    "student_email": request.user.email,
                    "register_as": "Tutor"
                    })
        registerEmail = EmailMessage(
            'Invitation Accepted',
            template,
            settings.EMAIL_HOST_USER,
            [invite.inivitaion_by_student.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        messages.info(request, f'Accepted Invitation Request from {std.first_name} {std.last_name}')
        return redirect("invitations")
    context = {
        "invite": invite
    }
    return render(request, 'tutors/accept_invitation.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def rejectInvite(request, id):
    invite = Invitaions.objects.get(id = id)

    tutor = Tutor.objects.get(username = request.user.username)
    student = Student.objects.get(username = invite.inivitaion_by_student.username)
    if request.method == "POST":
        invite.delete()

        tutor.invitations_recieved_rejected += 1
        tutor.save()
        student.invitations_sent_rejected += 1
        student.save()

        template = render_to_string("home/rejectEmail.html", {
                    "firstname": request.user.tutor.first_name,
                    "lastname": request.user.tutor.last_name,
                    "student_email": request.user.email
                    })
        registerEmail = EmailMessage(
            'Invitation Rejected',
            template,
            settings.EMAIL_HOST_USER,
            [invite.inivitaion_by_student.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        messages.warning(request, f'Rejected Invite From {student.first_name} {student.last_name}')
        return redirect("invitations")
    context = {
        "invite": invite
    }
    return render(request, 'tutors/reject_invite.html', context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def allStudents(request):
    students = PostAnAd_std.objects.all()
    tuition_level_contains_query = request.GET.get('TuitionLevel')
    subject_contains_query = request.GET.get('Subject')
    city_contains_query = request.GET.get('City')

    if students:
        if tuition_level_contains_query != "" and tuition_level_contains_query is not None and tuition_level_contains_query != "All":
            students = students.filter(tuition_level = tuition_level_contains_query)

        if subject_contains_query != "" and subject_contains_query is not None:
            students = students.filter(subject__icontains = subject_contains_query)

        if city_contains_query != "" and city_contains_query is not None:
            students = students.filter(studentUser__city__icontains = city_contains_query)

    context = {
        "students":students
    }
    return render(request, "tutors/all_students.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def specificStudent(request, id):
    student = PostAnAd_std.objects.get(id = id)
    student.views += 1
    student.save()
    students = PostAnAd_std.objects.filter(studentUser__username = student.studentUser.username).order_by("-id")
    context = {
        "student": student,
        "students":students.exclude(id = id)
    }
    return render(request, "tutors/specific_std.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def inviteForDemo(request, id):
    ad = PostAnAd_std.objects.get(id = id)

    std = Student.objects.get(username = ad.studentUser)

    tutor = Tutor.objects.get(tutor__username = request.user.username)

    try:
        invite_by_tutor = TutorInvitaions.objects.get(student_ad = ad)
    except:
        invite_by_tutor = None

    if request.method == "POST":
        if invite_by_tutor != None:
            if invite_by_tutor.invitation_sent == True and invite_by_tutor.inivitaion_by_tutor.username == request.user.username:
                messages.info(request, f'Already Asked {ad.studentUser.first_name} {ad.studentUser.last_name} for demo')
                return redirect("all_students")
            else:
                TutorInvitaions.objects.create(
                    inivitaion_by_tutor = tutor,
                    student_ad = ad,
                    invitation_sent = True,
                    accepted = False,
                    rejected = False
                )
                tutor.invitations_sent += 1
                tutor.save()
                std.invitations_recieved += 1
                std.save()

                template = render_to_string("home/inviteEmail.html", {
                    "firstname": ad.studentUser.first_name,
                    "lastname": ad.studentUser.last_name,
                    "ad": ad,
                    "invited_to": "Student"
                    })
                registerEmail = EmailMessage(
                    'Request A Demo',
                    template,
                    settings.EMAIL_HOST_USER,
                    [request.user.email]
                )
                registerEmail.fail_silently = False
                registerEmail.send()

                intemplate = render_to_string("home/invitationEmail.html", {
                    "firstname": request.user.tutor.first_name,
                    "lastname": request.user.tutor.last_name,
                    "ad": ad,
                    "invited_to": "Student"
                    })
                email = EmailMessage(
                    'Invitation',
                    intemplate,
                    settings.EMAIL_HOST_USER,
                    [ad.studentUser.email]
                )
                email.fail_silently = False
                email.send()

                messages.info(request, f'Asked {std.first_name} {std.last_name} For A Demo')
                return redirect("invited_students")
        else:
            TutorInvitaions.objects.create(
                    inivitaion_by_tutor = tutor,
                    student_ad = ad,
                    invitation_sent = True,
                    accepted = False,
                    rejected = False
                )
            tutor.invitations_sent += 1
            tutor.save()
            std.invitations_recieved += 1
            std.save()

            template = render_to_string("home/inviteEmail.html", {
                    "firstname": ad.studentUser.first_name,
                    "lastname": ad.studentUser.last_name,
                    "ad": ad,
                    "invited_to": "Student"
                    })
            registerEmail = EmailMessage(
                    'Request A Demo',
                    template,
                    settings.EMAIL_HOST_USER,
                    [request.user.email]
                )
            registerEmail.fail_silently = False
            registerEmail.send()

            intemplate = render_to_string("home/invitationEmail.html", {
                "firstname": request.user.tutor.first_name,
                "lastname": request.user.tutor.last_name,
                "ad": ad,
                "invited_to": "Student"
                })
            email = EmailMessage(
                'Invitation',
                intemplate,
                settings.EMAIL_HOST_USER,
                [ad.studentUser.email]
            )
            email.fail_silently = False
            email.send()


            messages.info(request, f'Asked {std.first_name} {std.last_name} For A Demo')
            return redirect("invited_students")
    context = {
        "ad":ad
    }
    return render(request, 'tutors/invite_for_demo.html', context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def tutorInvited(request):
    tutor = Tutor.objects.get(username = request.user.username)
    invited = TutorInvitaions.objects.filter(inivitaion_by_tutor = tutor)

    context = {
        "invited": invited
    }

    return render (request, 'tutors/invited.html', context)

from django.contrib.auth.models import User

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def about_qual (request):
    aboutForm = AboutForm()

    if request.method == "POST":
        aboutForm = AboutForm(request.POST)

        if aboutForm.is_valid():
            tagline = aboutForm.cleaned_data["tagline"]
            about = aboutForm.cleaned_data["about"]
            tut = Tutor.objects.get(username = request.user.username)
            tut.about = about
            tut.tagline = tagline
            tut.about_complete = True
            tut.save()

            return redirect('tutor_dashboard')

    context = {
        "about": aboutForm
    }
    return render (request, 'tutors/about_qual.html', context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def qual (request):
    form = QualificationForm()
    user = User.objects.get(username = request.user.username)
    tutor = user.tutor

    if request.method == "POST":
        form = QualificationForm(request.POST)
        if form.is_valid():

            try:
                AboutAndQualifications.objects.get(tutor__username = request.user.username).delete()
            except:
                pass

            
            highest_qual = form.cleaned_data["highest_qual"]
            highest_qual_inst = form.cleaned_data["highest_qual_inst"]
            secondary_qaul = form.cleaned_data["secondary_qaul"]
            secondary_qaul_inst = form.cleaned_data["secondary_qaul_inst"]

            AboutAndQualifications.objects.create(
                tutor= tutor,
                highest_qual = highest_qual,
                highest_qual_inst = highest_qual_inst,
                secondary_qaul = secondary_qaul,
                secondary_qaul_inst = secondary_qaul_inst
            )

            tut = Tutor.objects.get(username = request.user.username)
            tut.qual_complete = True
            if tut.verified:
                tut.verified = False
            tut.save()

            return redirect("tutor_dashboard")

    context = {
        "form":form
    }
    return render (request, "tutors/qual.html", context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def verifydoc (request):
    form = VerifyForm()
    user = User.objects.get(username = request.user.username)

    if request.method == "POST":
        form = VerifyForm(request.POST, request.FILES)

        if form.is_valid():


            try:
                Verify.objects.get(tutor__username = request.user.username).delete()
            except:
                pass

            cnic_front = form.cleaned_data["cnic_front"]
            cnic_back = form.cleaned_data["cnic_back"]
            highist_qual = form.cleaned_data["highest_qual"]
            Verify.objects.create(
                tutor = user.tutor,
                cnic_front = cnic_front,
                cnic_back = cnic_back,
                highist_qual= highist_qual
            )
            tutor = user.tutor
            tutor.verification_sent = True
            tutor.save()

            template = render_to_string("home/tutorVerify.html", {
                    "firstname": request.user.tutor.first_name,
                    "lastname": request.user.tutor.last_name,
                    "tutor_id": request.user.tutor.id,
                    "tutor_email": request.user.email
                    })
            registerEmail = EmailMessage(
                f'Tutor Verification: tutor ID {request.user.tutor.id}',
                template,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER]
            )
            registerEmail.fail_silently = False
            registerEmail.send()


            return redirect("tutor_dashboard")
    context = {
        "form": form
    }
    return render(request, "tutors/verify_doc.html", context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def del_account_student(request):
    tutor = User.objects.get(username = request.user.username)
    if request.method == "POST":
        tutor.is_active = False
        tutor.save()

        template = render_to_string("home/delEmail.html", {
                "register_as": "tutor",
                "email": request.user.email,
            })
        registerEmail = EmailMessage(
            'Account Deletion',
            template,
            settings.EMAIL_HOST_USER,
            [request.user.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        return redirect("tutor_dashboard")
    context = {}
    return render(request, "tutors/del_tutor.html", context)