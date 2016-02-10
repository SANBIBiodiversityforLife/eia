# Django rendering stuff
from django.shortcuts import render_to_response, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView

# Core & settings
from core import models, forms
from django.contrib.auth.models import Group


class ProfileUpdate(UpdateView):
    """
    Allows users to update their profile (django-allauth)
    """
    model = models.Profile
    template_name = 'account/profile_update.html'
    form_class = forms.ProfileUpdateForm

    # Get user from the request
    def get_object(self, queryset=None):
        return self.request.user.profile


def request_status(request, status):
    """
    Allows users on their profile page to request to be added to a group - e.g. trusted
    """
    # Retrieve the correct group for users, note the regex in the urls stops this being anything weird
    group = Group.objects.get(name=status)

    # Add the user to the group
    request.user.groups.add(group)

    # Redirect the user
    return redirect('profile_update')
