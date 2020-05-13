from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from students.models import Student

from django.core.mail import EmailMessage
from django.conf import settings 
from django.template.loader import render_to_string

#testing

from tutors.models import Tutor, AboutAndQualifications
# Create your views here.


def tutors(request):
    # allTutors = Tutor.objects.all().order_by("-id")
    # notVerified = 0
    # for t in allTutors:
    #     if not t.verified:
    #         notVerified += 1
    # number = allTutors.count()
    # if len(allTutors) > 1 and notVerified > 1:
    #     allTutors = None
    #     number = None

    try:
        allTutors = Tutor.objects.all().order_by("-id")
    except:
        allTutors = None
    tuts = []
    if allTutors != None:
        for t in allTutors:
            if t.verified and t.tutor.is_active:
                tuts.append(t)

    context = {
        "tutors":tuts,
        "number": len(tuts)
    }
    return render(request, "home/all_tuts.html", context)


def tutorDetail (request, id):
    tutor = Tutor.objects.get(id = id)
    qual = AboutAndQualifications.objects.get(tutor__username = tutor.username)
    context = {
        "tutor":tutor,
        "qual": qual
    }
    return render (request, "home/tut_detail.html", context)

def home(request):
    group = None
    
    name = request.GET.get('name')
    email = request.GET.get('email')
    message = request.GET.get('message')

    if request.method == "POST":
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
        return render("/")

    if request.user.groups.exists():
        group = request.user.groups.all()[0].name
    context = {
        'grp': group,
        "page":"home",
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