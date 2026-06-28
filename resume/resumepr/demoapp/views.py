from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail 
from django.conf import settings
from .models import Job, Application, User
from .utils import extract_text_from_pdf, compute_matching_score
from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib import messages


def welcome_view(request): return render(request, 'welcome.html')

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome.")
            return redirect('dashboard') if user.is_superuser or user.role == 'recruiter' else redirect('home')
    else: form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard') if user.is_superuser or user.role == 'recruiter' else redirect('home')
    else: form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('welcome')


@login_required
def home_view(request):
    if request.user.is_superuser or request.user.role == 'recruiter': return redirect('dashboard')
    return render(request, 'home.html', {'jobs': Job.objects.all().order_by('-id')})

@login_required
def dashboard_view(request):
    if request.user.is_superuser or request.user.role == 'recruiter':
        jobs = Job.objects.filter(recruiter=request.user)
        total_apps = Application.objects.filter(job__recruiter=request.user).count()
        shortlisted = Application.objects.filter(job__recruiter=request.user, status='Shortlisted').count()
        return render(request, 'recruiter_dashboard.html', {'jobs': jobs, 'total_apps': total_apps, 'shortlisted': shortlisted})
    else:
        return render(request, 'candidate_dashboard.html', {'applications': Application.objects.filter(candidate=request.user)})

@login_required
def post_job_view(request):
    if request.method == "POST":
        Job.objects.create(recruiter=request.user, title=request.POST.get('title'), 
                           description=request.POST.get('description'), requirements=request.POST.get('requirements'))
        return redirect('dashboard')
    return render(request, 'post_job.html')


@login_required
def apply_job_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == "POST" and request.FILES.get('resume'):
        resume = request.FILES['resume']
        raw_text = extract_text_from_pdf(resume)
        score, skills = compute_matching_score(raw_text, job.requirements)
        
        request.user.first_name, request.user.last_name = request.POST.get('first_name'), request.POST.get('last_name')
        request.user.save()
        
        Application.objects.create(
            job=job, candidate=request.user, resume=resume, extracted_skills=skills,
            match_score=score, status='Shortlisted' if score >= 60 else 'Pending',
            qualification=request.POST.get('qualification'), experience_years=request.POST.get('experience_years'),
            current_company=request.POST.get('current_company'), address=request.POST.get('address')
        )
        return redirect('dashboard')
    return render(request, 'apply_job.html', {'job': job})

@login_required
def run_ai_screening(request, job_id):
    job = get_object_or_404(Job, pk=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job)
    for app in applications:
        app.status = 'Shortlisted' if app.match_score >= 60 else 'Rejected'
        app.save()
    return redirect('view_applicants', job_id=job.id)

@login_required
def view_applicants(request, job_id):
   
    job = get_object_or_404(Job, pk=job_id) 
    return render(request, 'applicants_list.html', {
        'job': job, 
        'applicants': Application.objects.filter(job=job).order_by('-match_score')
    })

@login_required
def update_status(request, app_id, status):
    application = get_object_or_404(Application, pk=app_id)
    application.status = status
    application.save()

    subject = f"Update regarding your application for {application.job.title}"
    c_name = f"{application.candidate.first_name} {application.candidate.last_name}".strip()
    if not c_name: c_name = application.candidate.username

    if status.lower() == 'rejected':
        message = f"Hi {c_name},\n\nThank you for applying to DS Developer Pvt Ltd. After careful review, we regret to inform you that we are not moving forward with your application for the '{application.job.title}' position.\n\nBest of luck with your future endeavors.\n\nRegards,\nRecruitment Team"
    else:
        message = f"Hi {c_name},\n\nCongratulations! We are happy to inform you that your profile has been selected for the next round for the '{application.job.title}' position at DS Developer Pvt Ltd.\n\nWe will reach out to you soon with further details.\n\nRegards,\nRecruitment Team"

    try:
        sender_name = "DS Developer Pvt Ltd"
        from_email = f"{sender_name} <{settings.EMAIL_HOST_USER}>"
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[application.candidate.email],
            fail_silently=False 
        )
        print(f"✅ Success: Mail sent to {application.candidate.email}")
    except Exception as e:
        print(f"❌ MAIL ERROR: {e}")

    return redirect('view_applicants', job_id=application.job.id)