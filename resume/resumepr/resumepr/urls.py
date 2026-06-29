from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from demoapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome_view, name='welcome'),
    path('login/', vuews.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('post_job/', views.post_job_view, name='post_job'),
    path('job/apply/<init:job_id>/', views.apply_job_view, name='apply_job')
    path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('application/<int:app_id>/status/<str:status>/', views.update_status, name='update_status'),
    path('job/<int:job_id>/ai-screen/', views.run_ai_screening, name='run_ai_screening'),
]

#
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root-settings.MEDIA_ROOT)



