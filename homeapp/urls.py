from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('searching', views.searchTeacher, name="search"),
    path('listing', views.listing, name="listing"),
    path('profil', views.course_center_profile, name='course_center_profile'),
    path('getUser/<int:pk>', views.getUser, name="getUser"),
]
