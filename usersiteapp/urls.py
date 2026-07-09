from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>', views.index, name="usersite_home"),
    path('about/<int:pk>', views.about, name="about"),
    path('works/<int:pk>', views.work, name="work"),
    path('works/<int:pk>/<int:workId>', views.workDetails, name="workDetail"),
    path('contact/<int:pk>', views.contact, name="contact"),
    path('credentials/<int:pk>', views.credentials, name="credentials"),
    path('services/<int:pk>', views.services, name="services"),
]
