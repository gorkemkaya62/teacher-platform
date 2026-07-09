from django.urls import path
from . import views

urlpatterns = [
    # Admin Panel URLs
    path('adminpanel/login', views.admin_panel_login, name="admin_panel_login"),
    path('adminpanel/logout', views.admin_logout, name="admin_logout"),
    path('adminpanel/dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('adminpanel/user/<int:user_id>', views.admin_user_detail, name="admin_user_detail"),
    path('adminpanel/course-center/<int:course_center_id>', views.admin_course_center_detail, name="admin_course_center_detail"),
    path('adminpanel/user/<int:user_id>/delete', views.admin_delete_user, name="admin_delete_user"),
    path('adminpanel/course-center/<int:course_center_id>/delete', views.admin_delete_course_center, name="admin_delete_course_center"),

    path('login', views.adminlogin, name="login"),
    path('register', views.adminregister, name="register"),
    path('api/districts/', views.district_choices_api, name="district_choices_api"),
    path('loginout', views.loginout, name="logout"),
    path('adminlogout', views.adminlogout, name="adminlogout"),
    path('updatePassword', views.updatePassword, name="updatePassword"),
    path('forgotpassword', views.forgotPassword, name="forgotPassword"),

    # Öğretmen Profil Yönetimi
    path('add-items', views.addItems, name="addItems"),
    path('add-teacher-profile', views.teacherProfileAccept, name="teacherProfileAccept"),
    path('add-teacher-skill', views.teacherSkillAccept, name="teacherSkillAccept"),
    path('add-teacher-education', views.teacherEducationAccept, name="teacherEducationAccept"),
    path('add-teacher-experience', views.teacherExperienceAccept, name="teacherExperienceAccept"),
    path('add-teacher-service', views.teacherServiceAccept, name="teacherServiceAccept"),
    path('add-teacher-work', views.teacherWorkAccept, name="teacherWorkAccept"),
    path('add-teacher-certificate', views.teacherCertificateAccept, name="teacherCertificateAccept"),

    # Listing Area
    path('listing-skill', views.listingSkill, name="listingSkill"),
    path('listing-education', views.listingEducation, name="listingEducation"),
    path('listing-experience', views.listingExperience, name="listingExperience"),
    path('listing-service', views.listingService, name="listingService"),
    path('listing-work', views.listingWork, name="listingWork"),
    path('listing-award', views.listingAward, name="listingAward"),

    # Update Area
    path('updateSkill/<int:pk>', views.updateSkill, name="updateSkill"),
    path('updateEducation/<int:pk>', views.updateEducation, name="updateEducation"),
    path('updateExperience/<int:pk>', views.updateExperience, name="updateExperience"),
    path('updateService/<int:pk>', views.updateService, name="updateService"),
    path('updateWork/<int:pk>', views.updateWork, name="updateWork"),
    path('updateAward/<int:pk>', views.updateAward, name="updateAward"),

    # Delete Area
    path('deleteSkill/<int:pk>', views.deleteSkill, name="deleteSkill"),
    path('deleteEducation/<int:pk>', views.deleteEducation, name="deleteEducation"),
    path('deleteExperience/<int:pk>', views.deleteExperience, name="deleteExperience"),
    path('deleteService/<int:pk>', views.deleteService, name="deleteService"),
    path('deleteWork/<int:pk>', views.deleteWork, name="deleteWork"),
    path('deleteAward/<int:pk>', views.deleteAward, name="deleteAward"),
]
