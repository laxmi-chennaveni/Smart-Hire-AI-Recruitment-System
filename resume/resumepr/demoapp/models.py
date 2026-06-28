from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # 👈 AUTH_USER_MODEL లేదా settings వాడటానికి ఇది ముఖ్యం

# 1. కస్టమ్ యూజర్ మోడల్
class User(AbstractUser):
    IS_CANDIDATE = 'candidate'
    IS_RECRUITER = 'recruiter'
    ROLE_CHOICES = [
        (IS_CANDIDATE, 'Candidate'),
        (IS_RECRUITER, 'Recruiter'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=IS_CANDIDATE)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='demoapp_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='demoapp_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

# 2. జాబ్ పోస్టింగ్ మోడల్
class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'recruiter'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Comma separated skills")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 3. జాబ్ అప్లికేషన్ మోడల్ (కొత్త ఫీల్డ్స్ తో సహా)
class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected')
    ]
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    # ఇక్కడ నేరుగా User మోడల్‌ని లేదా settings.AUTH_USER_MODEL ని వాడుకోవచ్చు
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'candidate'})
    resume = models.FileField(upload_to='resumes/')
    extracted_skills = models.TextField(blank=True, null=True)
    match_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    # 🎯 కొత్తగా యాడ్ చేసిన క్వాలిఫికేషన్ & ఎక్స్‌పీరియన్స్ ఫీల్డ్స్:
    qualification = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    current_company = models.CharField(max_length=100, blank=True, null=True)
    present_ctc = models.CharField(max_length=50, blank=True, null=True)
    expected_ctc = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"