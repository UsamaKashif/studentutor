from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from students.models import Student
from django.contrib.auth.models import User

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

#testing

from tutors.models import Tutor, AboutAndQualifications, Invitaions
from tutors.models import PostAnAd as PostAnAd_tutor

from students.forms import StudentSignupForm
from django.contrib.auth.models import Group

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from students.utils import generate_token

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


def tutors(request):

    try:
        allTutors = Tutor.objects.all().order_by("-id")
    except:
        allTutors = None
    tuts = []
    if allTutors != None:
        for t in allTutors:
            if t.verified and t.tutor.is_active:
                tuts.append(t)

    tutors = PostAnAd_tutor.objects.all().order_by("-id")
    tuition_level_contains_query = request.GET.get('TuitionLevel')
    subject_contains_query = request.GET.get('Subject')
    city_contains_query = request.GET.get('City')

    number = tutors.count()

    paginator = Paginator(tuts,6)
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
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name

    context = {
        "tutors":tutors,
        "number": number,
        "tutor":tuts,
        "items": items,
        "page_range": page_range,
        "grp": group
    }
    return render(request, "home/all_tuts.html", context)

def ads_detail(request, id):
    tutor = PostAnAd_tutor.objects.get(id = id)
    qual = AboutAndQualifications.objects.get(tutor__username = tutor.tutorUser.username)
    tutor.views += 1
    tutor.save()
    tutors = PostAnAd_tutor.objects.filter(tutorUser__username = tutor.tutorUser.username).order_by("-id")
    
    try:
        registered = request.user.groups.all()[0].name
    except:
        registered = None

    form = StudentSignupForm()

    if request.method == "POST":
        form = StudentSignupForm(request.POST)

        if form.is_valid():
            student = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            age = form.cleaned_data.get('age')
            city = form.cleaned_data.get('city')
            firstName = form.cleaned_data.get('first_name')
            lastName = form.cleaned_data.get('last_name')
            phone = form.cleaned_data.get("phone")

            group = Group.objects.get(name="students")
            student.groups.add(group)

            Student.objects.create(
                student=student,
                username= username,
                email = email,
                age =age,
                city = city,
                first_name = firstName,
                last_name = lastName,
                phone = phone
            )

            student.is_active = False
            student.save()

            current_site = get_current_site(request)
            template = render_to_string("home/activate_invite_register.html", {
                "firstname": firstName,
                "lastname": lastName,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(student.pk)),
                "token": generate_token.make_token(student),
                "id":id
            })
            registerEmail = EmailMessage(
                'Account Activation',
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )
            registerEmail.fail_silently = False
            registerEmail.send()

            return render(request,"home/activation_sent.html",{})
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name

    context = {
        "tutor": tutor,
        "qual": qual,
        "tutors": tutors.exclude(id = id),
        "registered": registered,
        "form": form,
        "grp": group
    }
    return render (request,"home/ads_detail.html", context)


def activate_invite_view(request,uidb64, token, id):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        student = User.objects.get(pk = uid)
    except:
        student = None
    
    if student is not None and generate_token.check_token(student, token):
        student.is_active = True
        student.save()
        student = student.student
        template = render_to_string("home/registerEmail.html", {
            "firstname": student.first_name,
            "lastname": student.last_name,
            "register_as" : "student"
        })
        registerEmail = EmailMessage(
            'Registration Successful',
            template,
            settings.EMAIL_HOST_USER,
            [student.email]
        )
        registerEmail.fail_silently = False
        registerEmail.send()

        ad = PostAnAd_tutor.objects.get(id=id)
        tutor = Tutor.objects.get ( username = ad.tutorUser.username)
        

        
        Invitaions.objects.create(
                inivitaion_by_student = student,
                tutor_ad = ad,
                invitation_sent = True,
                accepted = False,
                rejected = False
            )
        student.invitations_sent += 1
        student.save()
        tutor.invitations_recieved += 1
        tutor.save()
        demotemplate = render_to_string("home/inviteEmail.html", {
                "firstname": ad.tutorUser.first_name,
                "lastname": ad.tutorUser.last_name,
                "ad": ad,
                "invited_to": "Tutor",
                "area":ad.address,
                "city":ad.tutorUser.city
                })
        demoEmail = EmailMessage(
                'Invite For Demo',
                demotemplate,
                settings.EMAIL_HOST_USER,
                [student.email]
            )
        demoEmail.fail_silently = False
        demoEmail.send()

        intemplate = render_to_string("home/invitationEmail.html", {
        "firstname": student.first_name,
        "lastname": student.last_name,
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


        messages.success(request,'account was created for ' + student.username)
        messages.success(request,'Invitation Sent To ' + tutor.tutor.first_name)
        return redirect("sign_in")


    return render(request, 'students/activate_failed.html', status=401)


def tutorDetail (request, id):
    tutor = Tutor.objects.get(id = id)
    ads = PostAnAd_tutor.objects.filter(tutorUser = tutor)
    qual = AboutAndQualifications.objects.get(tutor__username = tutor.username)

    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name
    context = {
        "tutor":tutor,
        "qual": qual,
        "ads": ads,
        "grp": group
    }
    return render (request, "home/tut_detail.html", context)

def home(request):
    group = None
    
    tutors = Tutor.objects.all().count()
    students = Student.objects.all().count()

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        template = render_to_string("home/contact.html", {
            "name": name,
            "email": email,
            "message": message
        })
        registerEmail = EmailMessage(
            'User Contact',
            template,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER]
        )
        registerEmail.fail_silently = False
        registerEmail.send()
        return redirect("home_page")

    if request.user.groups.exists():
        group = request.user.groups.all()[0].name

    context = {
        'grp': group,
        "page":"home",
        "tutors": tutors,
        "students": students
    }
    return render(request, 'home/index_page.html' , context)


def registerAs(request):
    context = {}
    return render(request,'home/register_as.html',context)


def signIn(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        student= authenticate(request, username=username, password=password)
        group = None
        


        if student is not None:
            login(request, student)
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                
            
            if group == "students": 
                return redirect('student_dashboard')
            else:
                return redirect("tutor_dashboard")
        else:
            messages.info(request, "username or password is incorrect")
            return redirect("sign_in")
    context = {}
    return render(request, 'home/sign_in.html', context)


def signOut(request):

    logout(request)
    return redirect("sign_in")


def privcy_policy(request):
    return render (request, "home/privacyPolicy.html",{})


def terms_of_use(request):
    return render (request, "home/terms.html",{})

