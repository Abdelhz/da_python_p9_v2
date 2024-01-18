from django import forms
from .models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        help_texts = {
            'title': 'Enter the title of your ticket.',
        }
        labels = {
            'image': 'Upload a cover image (optional)',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'headline', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5}),
        }
        help_texts = {
            'headline': 'Enter a headline for your review.',
            'rating': 'Rate the ticket from 0 to 5.',
        }
        labels = {
            'body': 'Write your review here (optional)',
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label="Nom d'utilisateur")
    password = forms.CharField(max_length=63, label="Mot de passe",
                               widget=forms.PasswordInput)
