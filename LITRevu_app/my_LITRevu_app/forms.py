from django import forms
from .models import Ticket, Review

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['your', 'fields', 'here']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['your', 'fields', 'here']