from django.shortcuts import render, redirect

from .forms import TutorSignUpform, TutorProfile, PostAnAdForm, QualificationForm, ProfilePicture, AboutForm, VerifyForm
from .models import Tutor, Invitaions, AboutAndQualifications, Verify,WishList,WishList_tut

from .models import PostAnAd as PostAnAd_tut

from students.models import PostAnAd as PostAnAd_std
from students.models import TutorInvitaions, Student,WishList_std

from django.contrib.auth.models import Group
from django.views.generic import RedirectView

from students.decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.core.mail import EmailMessage
from django.conf import settings 
from django.template.loader import render_to_string

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from students.utils import generate_token

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import threading 
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

            tutor.is_active = False
            tutor.save()

            current_site = get_current_site(request)

            template = render_to_string("tutors/activate.html", {
                "firstname": firstName,
                "lastname": lastName,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(tutor.pk)),
                "token": generate_token.make_token(tutor)
            })
            registerEmail = EmailMessage(
                'Account Activation',
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )
            registerEmail.fail_silently = False
            registerEmail.send()
            return render(request,"students/activation_sent.html",{})

            

    context = {
        "form": form,
    }
    return render(request, "tutors/tutor_register.html", context)


def activate_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        tutor = User.objects.get(pk = uid)
    except:
        tutor = None
    
    if tutor is not None and generate_token.check_token(tutor, token):
        tutor.is_active = True
        tutor.save()

        template = render_to_string("home/registerEmail.html", {
            "firstname": tutor.first_name,
            "lastname": tutor.last_name,
            "register_as" : "tutor"
        })
        registerEmail = EmailMessage(
            'Registration Successful',
            template,
            settings.EMAIL_HOST_USER,
            [tutor.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        messages.success(request,'account was created for ' + tutor.username)
        return redirect("sign_in")
    return render(request, 'students/activate_failed.html', status=401)


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

def post_ad(user,subject,tuition_level,can_travel,estimated_fees,address,tuition_type):
    ad = PostAnAd_tut(
        tutorUser = user,
        subject = subject,
        tuition_level = tuition_level,
        can_travel = can_travel,
        estimated_fees = estimated_fees,
        address = address,
        tuition_type = tuition_type
    )
    ad.save()
    user.total_ads += 1
    user.ad_post_count += 1
    user.save()

def email_send(user,emails,ad):
    if emails:
        template = render_to_string("home/tutorAD.html", {
        "firstname": user.first_name,
        "lastname": user.last_name,
        "ad":ad
        })
        ADEmail = EmailMessage(
            subject = f'{user.first_name} {user.last_name} posted an AD',
            body = template,
            from_email = settings.EMAIL_HOST_USER,
            bcc = emails
        )
        ADEmail.fail_silently = False
        ADEmail.send()


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def postAnAd(request, pk):
    postForm = PostAnAdForm()
    user = Tutor.objects.get(username = request.user.username)

    tutorAds = PostAnAd_tut.objects.filter(tutorUser__username = request.user.username)
    wishlist,created = WishList_std.objects.get_or_create(tutor=request.user.tutor)
    emails = []
    students = wishlist.students.all()
    for s in students:
        emails.append(s.email)

    if request.method == "POST":
        postForm = PostAnAdForm(request.POST)
        if postForm.is_valid():
            subject = postForm.cleaned_data['subject']
            tuition_level = postForm.cleaned_data['tuition_level']
            can_travel = postForm.cleaned_data['can_travel']
            estimated_fees = postForm.cleaned_data['estimated_fees']
            address = postForm.cleaned_data['address']
            tuition_type = postForm.cleaned_data["tuition_type"]

            adAvailabel = False

            for ad in tutorAds:
                if ad.subject == subject and ad.tuition_level == tuition_level:
                    adAvailabel = True
            
            if adAvailabel  == False:
                t1 = threading.Thread(target=post_ad, args=[user,subject,tuition_level,can_travel,estimated_fees,address,tuition_type])
                current_ad = {
                    "subject" : subject,
                    "tuition_level" : tuition_level,
                    "can_travel" : can_travel,
                    "estimated_fees" : estimated_fees,
                    "address" : address,
                    "tuition_type" : tuition_type  
                }
                t2 = threading.Thread(target=email_send, args=[user,emails,current_ad])
                
                t1.start()
                t2.start()

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
                    "email": request.user.email,
                    "register_as": "Tutor",
                    "phone": request.user.tutor.phone
                    })
        registerEmail = EmailMessage(
            'Invitation Accepted',
            template,
            settings.EMAIL_HOST_USER,
            [invite.inivitaion_by_student.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()
        
        
        recieve_temp = render_to_string("home/accept_recieve_Email.html", {
                    "request_from" : std,
                    "request": "Student"
                    })
        Email = EmailMessage(
            'Invitation Accepted',
            recieve_temp,
            settings.EMAIL_HOST_USER,
            [request.user.email]
        )
        Email.fail_silently = False
        Email.send()

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
    students = PostAnAd_std.objects.all().order_by("-id")
    tuition_level_contains_query = request.GET.get('TuitionLevel')
    subject_contains_query = request.GET.get('Subject')
    city_contains_query = request.GET.get('City')
    tuition_gender_query = request.GET.get('tuition_gender')

    number = students.count()

    if students:
        if tuition_level_contains_query != "" and tuition_level_contains_query is not None and tuition_level_contains_query != "All":
            students = students.filter(tuition_level = tuition_level_contains_query).order_by("-id")
            number = students.count()

        if subject_contains_query != "" and subject_contains_query is not None:
            students = students.filter(subject__icontains = subject_contains_query).order_by("-id")
            number = students.count()

        if city_contains_query != "" and city_contains_query is not None:
            students = students.filter(studentUser__city__icontains = city_contains_query).order_by("-id")
            number = students.count()

        if tuition_gender_query != "" and tuition_gender_query is not None and tuition_gender_query != "Both":
            students = students.filter(tutor_gender = tuition_gender_query)
            number = students.count()

    stds = []
    for s in students:
        if s.studentUser.profile_complete and s.studentUser.student.is_active:
            stds.append(s)
    number = len(stds)
    paginator = Paginator(stds,8)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    
    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    context = {
        "page_range": page_range,
        "items":items,
        "students":students,
        "number": number,
        "tutor":request.user.tutor
    }
    return render(request, "tutors/all_students.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def specificStudent(request, id):
    student = PostAnAd_std.objects.get(id = id)
    student.views += 1
    student.save()
    students = PostAnAd_std.objects.filter(studentUser__username = student.studentUser.username).order_by("-id")

    try:
        wishlist = WishList.objects.get(tutor=request.user.tutor)
    except:
        wishlist = None

    add = False
    if wishlist is not None:
        if student.studentUser in wishlist.students.all():
            add = True 

    context = {
        "student": student,
        "students":students.exclude(id = id),
        "tutor":request.user.tutor,
        "student_id":student.studentUser,
        "added":add
    }
    return render(request, "tutors/specific_std.html", context)

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["tutors"])
def inviteForDemo(request, id):
    ad = PostAnAd_std.objects.get(id = id)

    std = Student.objects.get(username = ad.studentUser.username)

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
                    "invited_to": "Student",
                    "area": ad.address,
                    "city":ad.studentUser.city
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
                    "invited_to": "Student",
                    "area": ad.address,
                    "city":ad.studentUser.city
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
                    "invited_to": "Student",
                    "area": ad.address,
                    "city":ad.studentUser.city
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
                "invited_to": "Student",
                "area": ad.address,
                "city":ad.studentUser.city
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
    invited = TutorInvitaions.objects.filter(inivitaion_by_tutor = tutor).order_by("-id")

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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

def add_like(post,tutor):
    post.likes.add(tutor)

def send_email(post,tutor):
    template = render_to_string("home/post_like_email.html", {
                "user":tutor,
                "post":post,
                "owner":post.studentUser
            })
    postLikeEmail = EmailMessage(
        f'{tutor.first_name} {tutor.last_name} liked your AD',
        template,
        settings.EMAIL_HOST_USER,
        [post.studentUser.email]
    )
    postLikeEmail.fail_silently = False
    postLikeEmail.send()




class PostLikeAPIToggle(APIView):

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None ,format=None):
        
        post = PostAnAd_std.objects.get(id=id)
        user = self.request.user
        tutor = user.tutor
        updated = False
        liked = False
        
        if tutor in post.likes.all():
            liked = False 
            updated = True
            post.likes.remove(tutor)
        else:
            liked =True 
            updated = True
            t1 = threading.Thread(target=add_like, args=[post,tutor])
            t2 = threading.Thread(target=send_email, args=[post,tutor])
            t1.start()
            t2.start()

            

        data = {
            "updated":updated,
            "liked":liked
        }
        return Response(data)


class WishlistApi(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None ,format=None):
        student = Student.objects.get(id=id)
        tutor = request.user.tutor
        updated = False 
        added = False 

        wishlist,created = WishList.objects.get_or_create(tutor=tutor)
        wishlist_tut,created = WishList_tut.objects.get_or_create(student=student)

        if student in wishlist.students.all():
            updated = True 
            added = False 
            wishlist.students.remove(student)
            wishlist_tut.tutors.remove(tutor)
        else:
            updated = True 
            added = True 
            wishlist.students.add(student)
            wishlist_tut.tutors.add(tutor)

        data = {
            "updated":updated,
            "added":added
        }
        return Response(data)


def wishList(request):
    try:
        wishlist = WishList.objects.get(tutor=request.user.tutor)
    except:
        wishlist = None 

    if wishlist is not None:
        students = wishlist.students.all()
    else:
        students = []

    context = {
        "students":students
    }
    return render(request,'tutors/wishlist.html',context)