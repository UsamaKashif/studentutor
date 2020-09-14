from django.shortcuts import render,redirect


from django.contrib.auth.models import Group
from .forms import AcademySignUpForm, AcademyProfile, ProfilePicture, PostAnAdForm, AboutAcademyForm

from django.contrib.auth.models import User
from django.views.generic import RedirectView

from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import login_required

from .models import Academy, PostAnAd, Invitations

from tutors.models import PostAnAd as PostAnAd_tutor



from tutors.models import PostAnAd as PostAnAd_tutor
from tutors.models import Invitaions,WishList_tut

from django.contrib import messages

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import threading



def academyRegister(request):
    form = AcademySignUpForm()

    if request.method == "POST":
        form = AcademySignUpForm(request.POST)

        if form.is_valid():
            academy = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            city = form.cleaned_data.get('city')
            phone = form.cleaned_data.get("phone")
            name = form.cleaned_data.get("name")
            address = form.cleaned_data.get("address")

            group = Group.objects.get(name="academy")
            academy.groups.add(group)

            Academy.objects.create(
                academy=academy,
                username= username,
                name=name,
                email = email,
                city = city,
                phone = phone,
                address= address
            )

            academy.is_active = False
            academy.save()

            current_site = get_current_site(request)

            template = render_to_string("academy/activate.html", {
                "name": name,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(academy.pk)),
                "token": generate_token.make_token(academy)
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
        "form": form
    }
    return render(request, 'academy/academy_sign_up.html', context)


def activate_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        academy = User.objects.get(pk = uid)
    except:
        academy = None

    if academy is not None and generate_token.check_token(academy, token):
        academy.is_active = True
        academy.save()

        template = render_to_string("academy/registerEmail.html", {
            "name": academy.name
        })
        registerEmail = EmailMessage(
            'Registration Successful',
            template,
            settings.EMAIL_HOST_USER,
            [academy.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        messages.success(request,'account was created for ' + academy.username)
        return redirect("sign_in")
    return render(request, 'students/activate_failed.html', status=401)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def academyDashboard(request):
    academy = request.user.academy


    form = AcademyProfile(instance=academy)

    user = Academy.objects.get(username = request.user.username)

    active_ads = PostAnAd.objects.filter(academyUser = request.user.academy).count()

    p_form = ProfilePicture()

    if request.method=="POST":
        form = AcademyProfile(request.POST,request.FILES, instance=academy)
        p_form = ProfilePicture(request.POST, request.FILES)

        if p_form.is_valid():
            image = p_form.cleaned_data["image"]
            std_image = Academy.objects.get(username = request.user.username)
            std_image.user_image = image
            std_image.save()

            return redirect("academy_dashboard")
        else:
            messages.warning(request, 'Supported File Extensions are .jpg And .png, Max Image Size Is 1MB')
            return redirect("academy_dashboard")

        if form.is_valid():
            form.save()

    context = {
        "form": form,
        "p_form": p_form,
        "totalAds": user.total_ads,
        "adsDel": user.ads_deleted,
        "activeAds": active_ads, # needs to be updated
        "invitations_sent": user.invitations_sent,
        "invitations_sent_accepted": user.invitations_sent_accepted,
        "invitations_sent_rejected": user.invitations_sent_rejected,
        "invitations_recieved": user.invitations_recieved,
        "invitations_recieved_accepted": user.invitations_recieved_accepted,
        "invitations_recieved_rejected": user.invitations_recieved_rejected,
    }
    return render(request, 'academy/academy_dashboard.html', context)


def post_ad(subject,tuition_level,hours_per_day,days_per_week,estimated_fees,user,tutor_gender):
    myad = PostAnAd(
        academyUser = user,
        subject = subject,
        tuition_level = tuition_level,        hours_per_day = hours_per_day,
        days_per_week = days_per_week,
        estimated_salary = estimated_fees,
        tutor_gender = tutor_gender
    )
    myad.save()
    user.total_ads += 1
    user.ad_post_count += 1
    user.save()

def email_send(user,my_ad,emails):
    if emails:
        template = render_to_string("home/stdAD.html", {
            "firstname": user.first_name,
            "lastname": user.last_name,
            "ad":my_ad
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
@allowed_users(allowed_roles=["academy"])
def postAd(request, pk):
    postform = PostAnAdForm()
    user = Academy.objects.get(username = request.user.username)


    academyAds = PostAnAd.objects.filter(academyUser__username = request.user.username)
    # wishlist,created = WishList_tut.objects.get_or_create(student=request.user.student)
    emails = []
    # tutors = wishlist.tutors.all()
    # for t in tutors:
    #     emails.append(t.email)

    if request.method == "POST":
        postform = PostAnAdForm(request.POST)


        if postform.is_valid():
            subject = postform.cleaned_data["subject"]
            tuition_level = postform.cleaned_data["tuition_level"]
            tutor_gender = postform.cleaned_data["tutor_gender"]
            hours_per_day = postform.cleaned_data["hours_per_day"]
            days_per_week = postform.cleaned_data["days_per_week"]
            estimated_salary = postform.cleaned_data["estimated_salary"]

            adAvailabel = False

            for ad in academyAds:
                if ad.subject == subject and ad.tuition_level == tuition_level:
                    adAvailabel = True
            if adAvailabel == False:
                currentad = {
                    "subject" : subject,
                    "tuition_level" : tuition_level,
                    "hours_per_day" : hours_per_day,
                    "days_per_week" : days_per_week,
                    "estimated_salary" : estimated_salary,
                    "tutor_gender":tutor_gender
                }
                my_ad = threading.Thread(target=post_ad, args=[subject,tuition_level,hours_per_day,days_per_week,estimated_salary,user,tutor_gender])

                # t2 = threading.Thread(target=email_send, args=[user,currentad,emails])

                my_ad.start()
                # t2.start()

                messages.info(request, "Your post is Successfully Created")
                return redirect("academy_dashboard")
            else:
                messages.info(request, "This AD Already Exists")
                return redirect("academy_dashboard")
    context = {
        "form": postform
    }
    return render(request, 'academy/post_ad.html', context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def Ads(request):
    try:
        studentAbout = AboutStudent.objects.get(student__username = request.user.username).order_by("-id")
    except:
        studentAbout = None
    ads = PostAnAd.objects.filter(academyUser=request.user.academy).order_by("-id")
    context = {
        "ads":ads,
        "about": studentAbout
    }
    return render(request, 'academy/ads.html', context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def AdsDelete(request, pk):

    ad = PostAnAd.objects.get(id=pk)

    user = Academy.objects.get(username=request.user.username)

    if request.method == "POST":
        ad.delete()
        user.ads_deleted += 1
        user.ad_post_count -= 1
        user.save()
        return redirect("ads_academy")
    context = {
        'ad':ad
    }
    return render(request, 'academy/delete_ad.html', context)


@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def allTutors(request):
    tutors = PostAnAd_tutor.objects.all().order_by("-id")
    tuition_level_contains_query = request.GET.get('TuitionLevel')
    subject_contains_query = request.GET.get('Subject')
    city_contains_query = request.GET.get('City')
    tuition_gender_query = request.GET.get('tuition_gender')
    number = tutors.count()

    if tutors:
        if tuition_level_contains_query != "" and tuition_level_contains_query is not None and tuition_level_contains_query != "All":
            tutors = tutors.filter(tuition_level = tuition_level_contains_query).order_by("-id")
            number = tutors.count()

        if subject_contains_query != "" and subject_contains_query is not None:
            tutors = tutors.filter(subject__icontains = subject_contains_query).order_by("-id")
            number = tutors.count()

        if city_contains_query != "" and city_contains_query is not None:
            tutors = tutors.filter(tutorUser__city__icontains = city_contains_query).order_by("-id")
            number = tutors.count()

        if tuition_gender_query != "" and tuition_gender_query is not None and tuition_gender_query != "Both":
            tutors = tutors.filter(tutorUser__gender__startswith = tuition_gender_query.lower())
            number = tutors.count()

    tuts = []
    if tutors:
        for t in tutors:
            tuts.append(t)

    paginator = Paginator(tuts,8)
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
        # "tutors":items,
        "items":items,
        "number": number,
        "academy": request.user.academy,
        "page_range": page_range,
    }
    return render(request, 'academy/all_tutors.html', context)


from tutors.models import AboutAndQualifications

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def SpecificTutor(request, id):
    tutor = PostAnAd_tutor.objects.get(id = id)
    qual = AboutAndQualifications.objects.get(tutor__username = tutor.tutorUser.username)
    tutor.views += 1
    tutor.save()
    tutors = PostAnAd_tutor.objects.filter(tutorUser__username = tutor.tutorUser.username).order_by("-id")

    # try:
    #     wishList = WishList.objects.get(student = request.user.student)
    # except:
    #     wishList = None

    # added = False
    # if wishList is not None:
    #     if tutor.tutorUser in wishList.tutors.all():
    #         added = True

    context = {
        "tutor_id": tutor.tutorUser,
        "tutor": tutor,
        "qual": qual,
        "tutors": tutors.exclude(id = id),
        "student": request.user.academy,
        "added":False, # needs to be updated
    }
    return render (request, "academy/specific_tutor.html", context)


from tutors.models import Tutor, Invitaions_by_academy

@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def inviteFordemo(request, id):
    ad = PostAnAd_tutor.objects.get(id = id)

    tutor = Tutor.objects.get ( username = ad.tutorUser.username)

    user = Academy.objects.get(username = request.user.username)

    std = Academy.objects.get(username = request.user.username)
    try:
        invites_sent_by_std = Invitaions_by_academy.objects.get(tutor_ad = ad)
    except:
        invites_sent_by_std = None

    if request.method == "POST":
        if invites_sent_by_std != None:
            if invites_sent_by_std.invitation_sent == True and invites_sent_by_std.inivitaion_by_academy.username == request.user.username:
                messages.info(request, f'Invitation request already sent to {ad.tutorUser.first_name} {ad.tutorUser.last_name}')
                return redirect("all_tutors_academy")
            else:
                Invitaions_by_academy.objects.create(
                    inivitaion_by_academy = std,
                    tutor_ad = ad,
                    invitation_sent = True,
                    accepted = False,
                    rejected = False
                )
                user.invitations_sent += 1
                user.save()
                tutor.invitations_recieved += 1
                tutor.save()

                template = render_to_string("home/inviteEmail.html", {
                    "firstname": ad.tutorUser.first_name,
                    "lastname": ad.tutorUser.last_name,
                    "ad": ad,
                    "invited_to": "Tutor",
                    "area":ad.address,
                    "city":ad.tutorUser.city
                    })
                registerEmail = EmailMessage(
                    'Invite For Demo',
                    template,
                    settings.EMAIL_HOST_USER,
                    [request.user.email]
                )
                registerEmail.fail_silently = False
                registerEmail.send()

                intemplate = render_to_string("academy/inviteEmail.html", {
                "firstname": request.user.academy.name,
                "ad": ad,
                "invited_to": "Tutor",
                "area":ad.address,
                "city":ad.tutorUser.city
                    })

                email = EmailMessage(
                    'Invitation',
                    intemplate,
                    settings.EMAIL_HOST_USER,
                    [ad.tutorUser.email]
                )
                email.fail_silently = False
                email.send()

                messages.info(request, f'Invited {tutor.first_name} {tutor.last_name} For A Demo')
                return redirect("academy_dashboard") # needs to be changes to invited page.

        else:
            Invitaions_by_academy.objects.create(
                    inivitaion_by_academy = std,
                    tutor_ad = ad,
                    invitation_sent = True,
                    accepted = False,
                    rejected = False
                )
            user.invitations_sent += 1
            user.save()
            tutor.invitations_recieved += 1
            tutor.save()



            template = render_to_string("home/inviteEmail.html", {
                "firstname": ad.tutorUser.first_name,
                "lastname": ad.tutorUser.last_name,
                "ad": ad,
                "invited_to": "Tutor",
                "area":ad.address,
                "city":ad.tutorUser.city
                })
            registerEmail = EmailMessage(
                'Invite For Demo',
                template,
                settings.EMAIL_HOST_USER,
                [request.user.email]
            )
            registerEmail.fail_silently = False
            registerEmail.send()

            intemplate = render_to_string("academy/inviteEmail.html", {
                "firstname": request.user.academy.name,
                "ad": ad,
                "invited_to": "Tutor",
                "area":ad.address,
                "city":ad.tutorUser.city
            })

            email = EmailMessage(
                'Invitation',
                intemplate,
                settings.EMAIL_HOST_USER,
                [ad.tutorUser.email]
            )
            email.fail_silently = False
            email.send()

            messages.info(request, f'Invited {tutor.first_name} {tutor.last_name} For A Demo')
            return redirect("academy_dashboard") # needs to be changed to invited page
    context = {
        "ad":ad
    }
    return render(request, 'academy/invite_for_demo.html', context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def invited(request):
    student = Academy.objects.get(username = request.user.username)
    invited = Invitaions_by_academy.objects.filter(inivitaion_by_academy = student).order_by("-id")
    context={
        "invited": invited,
    }
    return render(request, "academy/invited.html", context)




@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def invitationsAcademy(request):
    invites = Invitations.objects.filter(academy_ad__academyUser = request.user.academy).order_by("-id")
    context = {
        "invites":invites
    }

    return render(request, 'academy/invitations.html', context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def view_your_ad_acad(request, id):
    student_ad = Invitations.objects.get(id = id)
    try:
        tutors = PostAnAd_tutor.objects.filter(subject = student_ad.academy_ad.subject)[4]
    except:
        tutors = PostAnAd_tutor.objects.filter(subject = student_ad.academy_ad.subject)

    context = {
        "invite":student_ad,
        "tutors": tutors.exclude(tutorUser__username = student_ad.inivitaion_by_tutor.username)
    }
    return render(request,'academy/view_your_ad.html', context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def acceptInvitationAcademy(request, id):
    invite = Invitations.objects.get(id = id)

    student = Academy.objects.get(username = request.user.username)
    tutor = Tutor.objects.get(username = invite.inivitaion_by_tutor.username)
    if request.method == "POST":

        invite.accepted = True
        invite.rejected = False
        invite.save()
        student.invitations_recieved_accepted += 1
        student.save()
        tutor.invitations_sent_accepted += 1
        tutor.save()


        template = render_to_string("academy/acceptEmail.html", {
                    "name": request.user.academy.name,
                    "email": request.user.email,
                    "register_as": "Academy",
                    "phone": request.user.academy.phone
                    })
        registerEmail = EmailMessage(
            'Invitation Accepted',
            template,
            settings.EMAIL_HOST_USER,
            [invite.inivitaion_by_tutor.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        recieve_temp = render_to_string("academy/accept_recieve_Email.html", {
                    "request_from" :tutor,
                    "request": "Tutor"
                    })
        Email = EmailMessage(
            'Invitation Accepted',
            recieve_temp,
            settings.EMAIL_HOST_USER,
            [request.user.email]
        )
        Email.fail_silently = False
        Email.send()

        messages.info(request, f'Accepted Invitation Request from {tutor.first_name} {tutor.last_name}')
        return redirect("invitations_academy")
    context = {
        "invite":invite
    }

    return render(request, "academy/accept_invitation.html", context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def rejectInviteAcademy(request, id):
    invite = Invitations.objects.get(id = id)

    student = Academy.objects.get(username = request.user.username)
    tutor = Tutor.objects.get(username = invite.inivitaion_by_tutor.username)

    if request.method == "POST":
        invite.delete()
        student.invitations_recieved_rejected += 1
        student.save()

        tutor.invitations_sent_rejected += 1
        tutor.save()

        template = render_to_string("home/rejectEmail.html", {
                    "firstname": request.user.academy.name,
                    "student_email": request.user.email
                    })
        registerEmail = EmailMessage(
            'Invitation Rejected',
            template,
            settings.EMAIL_HOST_USER,
            [invite.inivitaion_by_tutor.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        messages.warning(request, f'Rejected Invite From {tutor.first_name} {tutor.last_name}')
        return redirect("invitations_academy")
    context = {
        "invite": invite
    }
    return render(request,'academy/reject_invitation.html', context)





@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def del_account_acad(request):
    student = User.objects.get(username = request.user.username)
    # print(request.user.student.first_name)
    if request.method == "POST":
        student.is_active = False
        student.save()

        template = render_to_string("home/delEmail.html", {
                "register_as": "Academy",
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


        return redirect("academy_dashboard")
    context = {}
    return render(request, "academy/del_account.html", context)



@login_required(login_url="sign_in")
@allowed_users(allowed_roles=["academy"])
def aboutAcademy(request):
    aboutForm  = AboutAcademyForm()


    if request.method == "POST":
        aboutForm = AboutAcademyForm(request.POST)
        if aboutForm.is_valid():
            # try:
            #     AboutStudent.objects.get(student__username = request.user.username).delete()
            # except:
            #     pass
            about = aboutForm.cleaned_data["textArea"]
            std = Academy.objects.get(username=request.user.username)
            std.profile_complete = True
            std.textArea = about
            std.save()
            return redirect("academy_dashboard")
    context = {
        "form": aboutForm
    }

    return render(request, "academy/student_about.html", context)
