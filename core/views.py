from django.shortcuts import render,redirect
from core.forms  import *
from core.models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
from django.conf import settings


# Create your views here.

def home(request):
    return  render(request, "home.html")

def signup_view(request):
    if request.method == 'POST':
        startups_form = StartUpsForm(request.POST)
        students_form = StudentsForm(request.POST)
        # print("hii....I am here..........")

        # Checking If Student is registered.
        if  students_form.is_valid():
            # print ("I am inside.............!!!")
            user = students_form.save()
            user.name = students_form.cleaned_data.get('name')
            user.roll_number = students_form.cleaned_data.get('roll_number')
            user.email = students_form.cleaned_data.get('email')
            user.phone_number = students_form.cleaned_data.get('phone_number')
            Students.objects.create(user=user,name=user.name,roll_number=user.roll_number,email=user.email, phone_number=user.phone_number)
            username = students_form.cleaned_data.get('username')
            password = students_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('stud_home',kwargs={'pk': user.id}))

        
        elif startups_form.is_valid():
            user = startups_form.save()
            user.POC = startups_form.cleaned_data.get('POC')
            user.email = startups_form.cleaned_data.get('email')
            StartUps.objects.create(user=user,POC=user.POC,email=user.email)
            username = startups_form.cleaned_data.get('username')
            password = startups_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('startup_home',kwargs={'pk': user.id}))
    else:
        startups_form = StartUpsForm()
        students_form = StudentsForm()
    forms = {
        'students_form': students_form,
        'startups_form': startups_form
    }
    return render(request, 'register.html',forms)

@login_required
def user_logout(request, **kwargs):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def stud_login(request):
    if request.method == 'POST':
        
        username = request.POST.get('student_id')
        
        password = request.POST.get('passwd')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('stud_home',kwargs={'pk': user.id}))
            else:
                messages.info(request, 'User is flagged Inactive. Drop mail to internfair.iitg@gmail.com to reactivate your account')
                return HttpResponseRedirect(reverse('home'))
        else:
            messages.info(request, 'Invalid login details given')
            return HttpResponseRedirect(reverse('home'))
    else:
        return render(request, 'home.html')

def stp_login(request):
    if request.method == 'POST':
        username = request.POST.get('startup_id')
        password = request.POST.get('passwd')
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('startup_home',kwargs={'pk': user.id}))
            else:
                messages.info(request, 'User is flagged Inactive. Drop mail to internfair.iitg@gmail.com to reactivate your account')
                return HttpResponseRedirect(reverse('home'))
        else:
            messages.info(request, 'Invalid login details given')
            return HttpResponseRedirect(reverse('home'))
    else:
        return render(request, 'home.html')

@login_required
def stud_home(request,**kwargs):
    current_user = request.user
  
    # Getting Student Details
    try:
        stud_object = Students.objects.get(user=current_user)
    except:
        messages.info(request,"Kindly Login in StartUp section")
        logout(request)
        return HttpResponseRedirect(reverse('home'))      
    
    # Getting List of Available Startups
    all_startups = StartUps.objects.all()

    # When new application is created
    if request.method == 'POST':
        
        form = ApplicationForm(request.POST,request.FILES)
        if form.is_valid():
           
            # app_form = form.save()
            profile = request.POST.get('profile')
            # print("Hiiii.....",profile)
            form.content = form.cleaned_data.get('content')
            # print("Hiiii.....",form.content)
            startup_user = request.POST.get('startupName')
            # print("Hiiii.....",startup_user)
            startup_obj = StartUps.objects.get(pk=int(startup_user))      
            intern_profile = InternDetails.objects.all().filter(startup=startup_obj,profile=profile)[0]
            Application.objects.create(student=stud_object,intern_pos=intern_profile,resume=request.FILES['resume'],content=form.content)
            return HttpResponseRedirect(reverse("stud_home",kwargs={ 'pk':stud_object.id }))
        
        elif request.POST.get('startup'):
            startup = request.POST.get('startup')
            profile = request.POST.get('my_profile')
            user = User.objects.get(username=startup)
            stp_obj = StartUps.objects.get(user=user)
            intern_pos = InternDetails.objects.get(startup=stp_obj,profile=profile)
            app_obj = Application.objects.get(student=stud_object, intern_pos=intern_pos)
            app_obj.delete()
            return HttpResponseRedirect(reverse("stud_home",kwargs={ 'pk':stud_object.id }))
            

    else :
        form = ApplicationForm()

    # List of applied Startups
    applied_startups = Application.objects.all().filter(student=stud_object)

    #Number of remaining applications 
    chances = int(MaxValue.objects.all()[0].limit) - applied_startups.count()
   
    all_intern_details = InternDetails.objects.all()

    
    context = {
        'student' : stud_object,
        'startups' : all_startups,
        'applied_startups' : applied_startups,
        'chances' : chances,
        'intern_detail': all_intern_details,
        'applied_startups':applied_startups,
        'form' : form,
    }
    return render(request,"Student_base.html",context)


@login_required
def startup_home(request,**kwargs):
    current_user = request.user
    # Getting StartUp Details
    try:
        stp_object = StartUps.objects.get(user=current_user)
    except:
        messages.info(request,"Kindly Login in Student Section")
        logout(request)
        return HttpResponseRedirect(reverse('home'))
    

    # List of positions created by startup
    intern_positions = InternDetails.objects.all().filter(startup=stp_object)

    # List of students applied to this startup
    application_objects = []
    selected_objs = []
    for intern_pos in intern_positions:
        application_objectss = Application.objects.all().filter(intern_pos=intern_pos)
        for application_object in application_objectss:
            if application_object.status == 'PENDING':
                application_objects+=[application_object]
            else:
                selected_objs += [application_object]
    
    
    
    # Updating Application Status
    if request.method == "POST":
        logo_form = LogoForm(request.POST, request.FILES)
        if  request.POST.get('btn'):
            status = request.POST.get('btn')
            student = request.POST.get('are_you_sure_prompt_student_name')
            position = request.POST.get('are_you_sure_prompt_student_position')
           
            user_obj = User.objects.get(username=student)
            stud_obj = Students.objects.get(user=user_obj)
            pos_obj = InternDetails.objects.get(startup=stp_object,profile=position)  
            app_obj = Application.objects.get(student=stud_obj,intern_pos=pos_obj)
            if status=='Shortlist':
                app_obj.status = 'SHORTLISTED'
                app_obj.save()
            else:
                app_obj.status = 'REJECTED'
                app_obj.save()
            return HttpResponseRedirect(reverse("startup_home",kwargs={ 'pk':stp_object.id }))
        elif request.POST.get('student'):
            student = request.POST.get('student')
            position = request.POST.get('pos')
            user_obj = User.objects.get(username=student)
            stud_obj = Students.objects.get(user=user_obj)
            pos_obj = InternDetails.objects.get(startup=stp_object,profile=position)  
            app_obj = Application.objects.get(student=stud_obj,intern_pos=pos_obj)
            app_obj.status = 'PENDING'
            app_obj.save()
            return HttpResponseRedirect(reverse("startup_home",kwargs={ 'pk':stp_object.id }))
           
        elif request.POST.get('Cname'):
            profile = request.POST.get('Cintern_positions')
            stipend = request.POST.get('Cstipend')
            location = request.POST.get('Clocation')
            allowances = request.POST.get('Callowances')
            InternDetails.objects.create(startup=stp_object,profile=profile,stipend=stipend,location=location,allowances=allowances)
            return HttpResponseRedirect(reverse("startup_home",kwargs={ 'pk':stp_object.id }))
        
        elif logo_form.is_valid():
            stp_object.logo =  logo_form.cleaned_data.get('logo')
            stp_object.save()
   
    else :
        logo_form = LogoForm()
    
    context = {
        "startup" : stp_object,
        "applied_students" : application_objects,
        "updated_students" : selected_objs,
        "logo_form" : logo_form,
    }
    return render(request,"Startup_base.html",context)

@login_required
def pdf_view(request,pk,path):
    filepath = os.path.join(settings.MEDIA_ROOT,path)
   
    return  FileResponse(open(filepath, 'rb'), content_type='application/pdf')
