from itertools import chain
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import CharField, Value
from django.shortcuts import render, redirect
from .models import Ticket, Review, UserFollows
from .forms import TicketForm, ReviewForm

def feed(request):
    review = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    #reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
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


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('home')  # Redirect to home or any other page
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
            return redirect('some_view')  # Redirect to some view after successful ticket addition
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
            return redirect('some_view')  # Redirect to some view after successful review addition
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
            return redirect('some_view')  # Redirect to a relevant view
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
    template_name = 'edit_ticket.html'
    
    def get_success_url(self):
        return reverse_lazy('my_LITRevu_app/tickets/ticket_edit.html', args=[self.object.id])


@method_decorator(login_required, name='dispatch')
class EditReviewView(UpdateView):
    model = Review
    fields = ['headline', 'body', 'rating']  # list all the fields that you want to be editable
    template_name = 'edit_review.html'
    
    def get_success_url(self):
        return reverse_lazy('my_LITRevu_app/reviews/review_edit.html', args=[self.object.id])


@login_required
def subscriptions(request):
    # Get the current user's following list
    following = UserFollows.objects.filter(user=request.user).select_related('followed_user')
    following_list = [user_follow.followed_user for user_follow in following]
    
    return render(request, 'my_LITRevu_app/subscriptions.html', {'following_list': following_list})