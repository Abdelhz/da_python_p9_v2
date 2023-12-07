from itertools import chain
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import CharField, Value
from django.shortcuts import render, redirect
from .models import Ticket, Review, UserFollows
from .forms import TicketForm, ReviewForm, LoginForm

def feed(request):
    def get_users_viewable_reviews(user):
        # Get reviews from users that the current user is following
        following_users = UserFollows.objects.filter(user=user).values('followed_user')
        return Review.objects.filter(user__in=following_users)

    def get_users_viewable_tickets(user):
        # Get tickets from users that the current user is following
        following_users = UserFollows.objects.filter(user=user).values('followed_user')
        return Ticket.objects.filter(user__in=following_users)

    reviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = review.annotate(content_type=Value('REVIEW', CharField()))
    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    # combine and sort the two types of posts

    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
        )
    
    return render(request, 'my_LITRevu_app/feed.html', context={'posts': posts})

def login_page(request):
    form = LoginForm()
    message = ""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                message = f"Bonjour, {user.username}! Vous êtes connecté"
                return redirect('feed')  # Redirect to home or any other page
            else:
                message = "Identifiants invalides"
    return render(request, 'registration/login.html', context={'form': form, 'message': message})

@login_required
def logout_user(request):
    
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('feed')  # Redirect to home or any other page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})




@login_required
def add_ticket(request):
    if request.method == 'POST':
        # You need to define a form for adding tickets
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('posts')  # Redirect to some view after successful ticket addition
    else:
        form = TicketForm()
    return render(request, 'my_LITRevu_app/tickets/add_ticket.html', {'form': form})


@login_required
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'my_LITRevu_app/tickets/view_ticket.html', {'ticket': ticket})


@login_required
def add_review(request):
    if request.method == 'POST':
        # You need to define a form for adding reviews
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('posts')  # Redirect to some view after successful review addition
    else:
        form = ReviewForm()
    return render(request, 'my_LITRevu_app/reviews/add_review.html', {'form': form})


@login_required
def view_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'my_LITRevu_app/reviews/view_review.html', {'review': review})


@login_required
def add_review_to_ticket(request, ticket_id):
    # Trying news add_review function
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('posts')  # Redirect to a relevant view
    else:
        form = ReviewForm()
    return render(request, 'my_LITRevu_app/reviews/add_review_to_ticket.html', {'form': form})


@login_required
def posts(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    return render(request, 'my_LITRevu_app/posts.html', {'tickets': tickets, 'reviews': reviews})


@method_decorator(login_required, name='dispatch')
class EditTicketView(UpdateView):
    model = Ticket
    fields = ['title', 'description']  # list all the fields that you want to be editable
    template_name = 'ticket_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('my_LITRevu_app/tickets/ticket_edit.html', args=[self.object.id])


@method_decorator(login_required, name='dispatch')
class EditReviewView(UpdateView):
    model = Review
    fields = ['headline', 'body', 'rating']  # list all the fields that you want to be editable
    template_name = 'review_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('my_LITRevu_app/reviews/review_edit.html', args=[self.object.id])


@login_required
def subscriptions(request):
    # Get the current user's following list
    following = UserFollows.objects.filter(user=request.user).select_related('followed_user')
    following_list = [user_follow.followed_user for user_follow in following]
    
    return render(request, 'my_LITRevu_app/subscriptions.html', {'following_list': following_list})

@login_required
def follow_user(request, user_id):
    User = get_user_model()
    if request.method == "POST":
        user_to_follow = get_object_or_404(User, id=user_id)
        # Check if the user already follows the other user
        followed_user, created = UserFollows.objects.get_or_create(user=request.user, followed_user=user_to_follow)
        if created:
            messages.success(request, "You are now following {}.".format(user_to_follow.username))
        else:
            messages.info(request, "You already follow {}.".format(user_to_follow.username))
    return HttpResponseRedirect(reverse('subscriptions'))

@login_required
def unfollow_user(request, user_id):
    User = get_user_model()
    if request.method == "POST":
        user_to_unfollow = get_object_or_404(User, id=user_id)
        UserFollows.objects.filter(user=request.user, followed_user=user_to_unfollow).delete()
        messages.success(request, "You have unfollowed {}.".format(user_to_unfollow.username))
    return HttpResponseRedirect(reverse('subscriptions'))

