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
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views

urlpatterns = [

    # User-related URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),

    # User-related Actions URLs
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),

    # Ticket-related URLs (assuming you'll implement these views)
    path('add_ticket/', views.add_ticket, name='add_ticket'),
    path('tickets/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
    path('edit_ticket/<int:pk>/', views.EditTicketView.as_view(),
         name='edit_ticket'),
    path('delete_ticket/<int:ticket_id>/', views.delete_ticket,
         name='delete_ticket'),

    # Review-related URLs
    path('add_review/', views.add_review, name='add_review'),
    path('add_review_to_ticket/<int:ticket_id>/', views.add_review_to_ticket,
         name='add_review_to_ticket'),

    path('reviews/<int:review_id>/', views.view_review, name='view_review'),

    path('edit_review/<int:pk>/', views.EditReviewView.as_view(),
         name='edit_review'),

    path('delete_review/<int:review_id>/', views.delete_review,
         name='delete_review'),

    # general_info_displayer URLs
    path('posts/', views.posts, name='posts'),
    path('feed/', views.feed, name='feed'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('search_user/', views.search_user, name='search_user'),
]

if settings.DEBUG:
    # Serving media files if DEBUG is set to True
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

else:
    # Serving static files if DEBUG is set to False
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

    # Serving media files if DEBUG is set to False
    urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve,
                    {'document_root': settings.MEDIA_ROOT, })]
