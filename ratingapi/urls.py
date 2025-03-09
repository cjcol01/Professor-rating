from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # auth endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    
    # API endpoints
    path('modules/instances/', views.ModuleInstanceListView.as_view(), name='module-instance-list'),
    path('professors/ratings/', views.ProfessorRatingListView.as_view(), name='professor-ratings'),
    path('ratings/create/', views.RatingCreateView.as_view(), name='rating-create'),
    path('professors/<str:professor_id>/modules/<str:module_code>/rating/', 
         views.professor_module_average_rating, name='professor-module-rating'),

    # my silly little goofy little homepage
    path('', views.home, name='home'),
]
