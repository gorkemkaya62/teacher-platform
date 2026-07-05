from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Ana sayfa için URL pattern
    path('searching', views.searchTeacher, name="search"),
    path('listing', views.listing, name="listing"),
    path('getUser/<int:pk>', views.getUser, name="getUser")
]
