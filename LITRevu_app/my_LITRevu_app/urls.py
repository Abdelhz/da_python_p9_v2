"""
URL configuration for LITRevu_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
 
    # User-related URLs
    path('register/', views.register, name='register'),
    #path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),

    #User-related Actions URLs
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

    # Ticket-related URLs (assuming you'll implement these views)
    path('add_ticket/', views.add_ticket, name='add_ticket'),
    path('tickets/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
    path('edit_ticket/<int:pk>/', views.EditTicketView.as_view(), name='edit_ticket'),
    path('delete_ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    # Review-related URLs
    path('add_review/', views.add_review, name='add_review'),
    path('reviews/<int:review_id>/', views.view_review, name='view_review'),
    path('edit_review/<int:pk>/', views.EditReviewView.as_view(), name='edit_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

    # general_info_displayer URLs
    path('posts/', views.posts, name='posts'),
    path('feed/', views.feed, name='feed'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    
    # Other URLs for your app can be added here as needed

    
]
