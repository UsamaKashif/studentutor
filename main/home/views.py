from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from students.models import Student

#testing

from tutors.models import Tutor, AboutAndQualifications
# Create your views here.


def tutors(request):
    allTutors = Tutor.objects.all()
    notVerified = 0
    for t in allTutors:
        if not t.verified:
            notVerified += 1

    if len(allTutors) > 1 and notVerified > 1:
        allTutors = None

    context = {
        "tutors":allTutors
    }
    return render(request, "home/all_tuts.html", context)

def zoho(request):
    context = {}
    return render(request,"home/verifyforzoho.html",context)

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
    tutors = Tutor.objects.all().order_by('-invitations_recieved')[:4]

    if not(len(tutors) >=3) :
        tutors = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name
    context = {
        'grp': group,
        "page":"home",
        "tutors": tutors
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
