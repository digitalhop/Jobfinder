from django.urls import path
from . import views

urlpatterns = [
    path('',views.jobs_view, name='jobs_view'),
    path('undecided_jobs/',views.jobs_undecided_view, name='undecided_jobs'),
    path('job_searches/',views.jobs_searches_view, name='jobs_searches'),
    path('unliked_jobs/',views.jobs_unliked, name='jobs_unliked')
]
