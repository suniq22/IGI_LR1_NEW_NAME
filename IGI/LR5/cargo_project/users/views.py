"""Auth views: signup, profile."""
import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, SignUpForm

logger = logging.getLogger('users')


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        logger.info('New user registered: %s', user.username)
        messages.success(request, 'Регистрация прошла успешно!')
        return redirect('users:profile')
    return render(request, 'users/signup.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user_obj': request.user})


@login_required
def profile_update(request):
    profile = request.user.profile
    form = ProfileUpdateForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён')
        return redirect('users:profile')
    return render(request, 'users/profile_form.html', {'form': form})
