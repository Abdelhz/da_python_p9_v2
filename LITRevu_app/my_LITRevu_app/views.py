from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import (get_user_model, login, authenticate,
                                 logout, update_session_auth_hash)

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import CharField, Value, Q
from django.shortcuts import render, redirect
from .models import Ticket, Review, UserFollows, UserBlock
from .forms import TicketForm, ReviewForm, LoginForm
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


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
                # Redirect to home or any other page
                return redirect('feed')
            else:
                message = "Identifiants invalides"
    return render(request, 'registration/login.html', context={'form': form,
                  'message': message})


@login_required(login_url='login')
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
            # Redirect to home or any other page
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important, to update the session with the new password
            update_session_auth_hash(request, user)

            messages.success(request,
                             'Your password was successfully updated!')

            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/profile.html', {'form': form})


@login_required(login_url='login')
def feed(request):
    def get_users_viewable_reviews(user):
        # Get reviews from users that the current user is following

        following_users = UserFollows.objects.filter(user=user).values(
            'followed_user')

        return Review.objects.filter(user__in=following_users)

    def get_users_viewable_tickets(user):
        # Get tickets from users that the current user is following

        following_users = UserFollows.objects.filter(user=user).values(
            'followed_user')

        tickets = Ticket.objects.filter(user__in=following_users).order_by(
            '-time_created')

        for ticket in tickets:
            ticket.can_add_review = (
                ticket.review_set.filter(user=user).exists())
        return tickets

    # returns queryset of reviews from users that the current user is following
    reviews = get_users_viewable_reviews(request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    # returns queryset of reviews made to tickets owned by the current user
    # except reviews made by the current user to its own tickets
    reviews_to_my_tickets = (Review.objects.filter(ticket__user=request.user)
                             .exclude(user=request.user))

    # combine and sort the two types of reviews
    reviews_followed = (reviews | reviews_to_my_tickets).distinct().order_by(
        '-time_created')

    # returns queryset of tickets from users that the current user is following
    tickets_followed = get_users_viewable_tickets(request.user)
    tickets_followed = (tickets_followed
                        .annotate(content_type=Value('TICKET', CharField())))

    # returns queryset of tickets owned by the current user
    user_tickets = Ticket.objects.filter(user=request.user).order_by(
        '-time_created')
    user_tickets = (user_tickets
                    .annotate(content_type=Value('TICKET', CharField())))

    # returns queryset of reviews made by the current user
    user_reviews = Review.objects.filter(user=request.user).order_by(
        '-time_created')
    user_reviews = (user_reviews
                    .annotate(content_type=Value('REVIEW', CharField())))

    context = {"user_tickets": user_tickets, "user_reviews": user_reviews,
               "reviews": reviews, "tickets": tickets_followed,
               "reviews_followed": reviews_followed,
               "tickets_followed": tickets_followed, "user": request.user}

    return render(request, 'my_LITRevu_app/feed.html', context)


@login_required(login_url='login')
def posts(request):
    tickets = Ticket.objects.filter(user=request.user).order_by(
        '-time_created')

    # returns queryset of tickets owned by the current user
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews = Review.objects.filter(user=request.user).order_by(
        '-time_created')

    # returns queryset of reviews made by the current user
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    return render(request, 'my_LITRevu_app/posts.html', {'tickets': tickets,
                  'reviews': reviews})


@login_required(login_url='login')
def add_ticket(request):
    if request.method == 'POST':
        # You need to define a form for adding tickets
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ticket = form.save(commit=False)
                ticket.user = request.user
                ticket.save()
                # Redirect to some view after successful ticket addition
                return redirect('posts')
            except IntegrityError:
                form.add_error('title', 'This ticket already exists.')
    else:
        form = TicketForm()
    return render(request, 'my_LITRevu_app/tickets/add_ticket.html',
                  {'form': form})


@login_required(login_url='login')
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    my_reviews = (Review.objects.filter(ticket=ticket, user=request.user)
                  .order_by('-time_created'))

    other_reviews = (Review.objects.filter(ticket=ticket)
                     .exclude(user=request.user).order_by('-time_created'))

    context = {'ticket': ticket, 'my_reviews': my_reviews,
               'other_reviews': other_reviews, 'user': request.user}

    return render(request, 'my_LITRevu_app/tickets/view_ticket.html', context)


@login_required(login_url='login')
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user != ticket.user:
        return HttpResponseForbidden(
            "You are not authorized to delete this ticket.")

    if request.method == 'POST':
        ticket.delete()
        return redirect('posts')  # Redirect to a relevant view
    return HttpResponseForbidden("Invalid request method.")


@login_required(login_url='login')
def add_review(request):
    if request.method == 'POST':
        form_review = ReviewForm(request.POST)
        form_ticket = TicketForm(request.POST)
        title = request.POST.get('title')
        try:
            ticket = Ticket.objects.get(title=title, user=request.user)
        except Ticket.DoesNotExist:
            # If the ticket does not exist, create a new one
            # check if the review form is valid
            if form_ticket.is_valid():
                ticket = form_ticket.save(commit=False)
                ticket.user = request.user
                ticket.save()
            else:
                logger.warning(
                    f"TicketForm is not valid: {form_ticket.errors}")

                return render(request,
                              'my_LITRevu_app/reviews/add_review.html',
                              {'form_review': form_review,
                               'form_ticket': form_ticket})

        # check if the review form is valid
        if form_review.is_valid():
            logger.info("Form is valid")
            # Create the new review
            review = form_review.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            # Redirect to posts after successful review addition
            return redirect('posts')
        else:
            logger.warning(f"ReviewForm is not valid: {form_review.errors}")
    else:
        form_review = ReviewForm()
        form_ticket = TicketForm()

    return render(request, 'my_LITRevu_app/reviews/add_review.html',
                  {'form_review': form_review, 'form_ticket': form_ticket})


@login_required(login_url='login')
def view_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    return render(request, 'my_LITRevu_app/reviews/view_review.html',
                  {'review': review, 'user': request.user})


@login_required(login_url='login')
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
            # Redirect to a relevant view
            return redirect('posts')
    else:
        form = ReviewForm()
    return render(request, 'my_LITRevu_app/reviews/add_review_to_ticket.html',
                  {'form': form, 'ticket': ticket})


@login_required(login_url='login')
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return HttpResponseForbidden(
            "You are not authorized to delete this review.")

    if request.method == 'POST':
        review.delete()
        return redirect('view_ticket', ticket_id=review.ticket.id)
    return HttpResponseForbidden("Invalid request method.")


@method_decorator(login_required, name='dispatch')
class EditTicketView(UpdateView):
    model = Ticket

    # list all the fields that you want to be editable
    fields = ['title', 'description', 'image']
    template_name = 'my_LITRevu_app/tickets/edit_ticket.html'

    def get_success_url(self):
        return reverse_lazy('view_ticket', args=[self.object.id])


@method_decorator(login_required, name='dispatch')
class EditReviewView(UpdateView):
    model = Review
    # list all the fields that you want to be editable
    fields = ['headline', 'body', 'rating']
    template_name = 'my_LITRevu_app/reviews/edit_review.html'

    def get_success_url(self):
        return reverse_lazy('view_review', args=[self.object.id])


@login_required(login_url='login')
def subscriptions(request):
    # Get the current user's following list
    following = UserFollows.objects.filter(user=request.user).select_related(
        'followed_user')

    following_list = [user_follow.followed_user for user_follow in following]

    # Get the users that are blocked by the current user
    blocked_users = (UserBlock.objects.filter(user_blocking=request.user)
                     .select_related('user_blocked'))
    blocked_list = [user_block.user_blocked for user_block in blocked_users]

    return render(request, 'my_LITRevu_app/subscriptions.html',
                  {'following_list': following_list,
                   'blocked_list': blocked_list})


@login_required(login_url='login')
def search_user(request):
    User = get_user_model()
    query = request.GET.get('username')
    following = UserFollows.objects.filter(user=request.user).select_related(
        'followed_user')

    following_list = [user_follow.followed_user for user_follow in following]
    blocking = (UserBlock.objects.filter(user_blocking=request.user)
                .values_list('user_blocked', flat=True))

    blocked_by = (UserBlock.objects.filter(user_blocked=request.user)
                  .values_list('user_blocking', flat=True))
    if query:
        users = (User.objects.filter(Q(username__istartswith=query))
                 .exclude(id=request.user.id))
    else:
        users = User.objects.none()

    return render(request, 'my_LITRevu_app/search_results.html',
                  {'users': users, 'following_list': following_list,
                   'blocking': blocking, 'blocked_by': blocked_by})


@login_required(login_url='login')
def follow_user(request, user_id):
    User = get_user_model()
    if request.method == "POST":
        user_to_follow = get_object_or_404(User, id=user_id)
        if (UserBlock.objects
            .filter(user_blocking=request.user, user_blocked=user_to_follow)
            .exists() or UserBlock.objects
                .filter(user_blocking=user_to_follow,
                        user_blocked=request.user).exists()):

            messages.error(request,
                           ("You can't follow this user because "
                            "one of you has blocked the other."))
            return HttpResponseRedirect(reverse('search_user'))
        try:
            # Check if the user already follows the other user
            followed_user, created = (
                UserFollows.objects
                .get_or_create(user=request.user,
                               followed_user=user_to_follow))

            if created:
                messages.success(request, "You are now following {}."
                                 .format(user_to_follow.username))

            else:
                messages.info(request, "You already follow {}."
                              .format(user_to_follow.username))

        except IntegrityError:
            messages.error(request, "You are already following {}."
                           .format(user_to_follow.username))

        # Get the current search query
        query = request.POST.get('username', '')
        if query is None:
            query = ''
        # Redirect to the 'search_user' page with the current search query
        return HttpResponseRedirect(reverse('search_user') +
                                    '?username=' + query)


@login_required(login_url='login')
def unfollow_user(request, user_id):
    User = get_user_model()
    if request.method == "POST":
        user_to_unfollow = get_object_or_404(User, id=user_id)
        UserFollows.objects.filter(user=request.user,
                                   followed_user=user_to_unfollow).delete()

        messages.success(request, "You have unfollowed {}."
                         .format(user_to_unfollow.username))

        # Get current page
        source_page = request.POST.get('source_page')
        # Log the source_page variable
        logger.warning('source_page: %s', source_page)

        if source_page == '/subscriptions/':
            # Redirect to the 'subscriptions' page
            return HttpResponseRedirect(reverse('subscriptions'))
        else:
            # Get the current search query
            query = request.POST.get('username')
            if query is None:
                query = ''
            # Redirect to the 'search_user' page with the current search query
            return HttpResponseRedirect(reverse('search_user') +
                                        '?username=' + query)


@login_required(login_url='login')
def block_user(request, user_id):
    User = get_user_model()
    if request.method == "POST":
        user_to_block = get_object_or_404(User, id=user_id)
        UserBlock.objects.create(user_blocking=request.user,
                                 user_blocked=user_to_block)

        UserFollows.objects.filter(user=request.user,
                                   followed_user=user_to_block).delete()

        UserFollows.objects.filter(user=user_to_block,
                                   followed_user=request.user).delete()

        # Get current page
        source_page = request.POST.get('source_page')
        if source_page == '/subscriptions/':
            # Redirect to the 'subscriptions' page
            return HttpResponseRedirect(reverse('subscriptions'))
        else:
            # Get the current search query
            query = request.POST.get('username')
            if query is None:
                query = ''
            # Redirect to the 'search_user' page with the current search query
            return HttpResponseRedirect(reverse('search_user') +
                                        '?username=' + query)


@login_required(login_url='login')
def unblock_user(request, user_id):
    User = get_user_model()
    if request.method == "POST":
        user_to_unblock = get_object_or_404(User, id=user_id)
        UserBlock.objects.filter(user_blocking=request.user,
                                 user_blocked=user_to_unblock).delete()

        # Get current page
        source_page = request.POST.get('source_page')

        if source_page == '/subscriptions/':
            # Redirect to the 'subscriptions' page
            return HttpResponseRedirect(reverse('subscriptions'))
        else:
            # Get the current search query
            query = request.POST.get('username', '')
            if query is None:
                query = ''
            # Redirect to the 'search_user' page with the current search query
            return HttpResponseRedirect(reverse('search_user') +
                                        '?username=' + query)
