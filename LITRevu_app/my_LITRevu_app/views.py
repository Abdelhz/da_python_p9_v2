from itertools import chain

from django.db.models import CharField, Value
from django.shortcuts import render


def feed(request):
    eviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    # combine and sort the two types of posts

    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
        )
    
    return render(request, 'feed.html', context={'posts': posts})