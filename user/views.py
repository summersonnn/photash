from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .forms import LoginForm, RegisterForm, ProfileForm, LanguageSelectionForm
from .tokens import account_activation_token
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.db import transaction
from django.urls import reverse
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import Permission
from user.models import Notification

def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if(user.is_active == False):
            return render(request, 'accounts/you_are_banned.html')
        else:
            login(request, user)
        username = User.objects.get(username=request.user)
        url = reverse('home')
        messages.success(request, "Welcome again " + str(username) + "!", extra_tags="alert-success")
        return HttpResponseRedirect(url)
    return render(request, 'accounts/form.html', {'form': form, 'title': 'Login'})

def activate_account(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    user = get_object_or_404(User, id=uid)

    #Önceden aktive edildiyse 404 verelim
    if user.profile.email_verified == True:
        return HttpResponseNotFound('<h1>No Page Here</h1>')

    if user is not None and not account_activation_token.check_token(user, token):
        return HttpResponseRedirect('/')

    #Email verification in database
    profile = user.profile
    profile.email_verified = True
    profile.save()

    #Giving permissions
    permission1 = Permission.objects.get(name='Can add new photos?')
    permission2 = Permission.objects.get(name='Can vote photos?')
    user.user_permissions.add(permission1)
    user.user_permissions.add(permission2)

    #Creating a notification for letting the user know he verified.
    verified = Notification(user=user, msg="You have successfully verified your account. You can now upload photos to a contest as well as vote the photos of others.")
    verified.save()

    login(request,user,backend='django.contrib.auth.backends.ModelBackend')
    return render(request, 'user/verification_done.html')


def logout_view(request):
    logout(request)
    messages.success(request, "See you next time fella!",  extra_tags="alert-danger")
    return redirect('home')


# --------------------------------------------------------------------------------------------
def profile_view(request):

    #Dil seçimi
    form = LanguageSelectionForm(data=request.POST or None)
    if form.is_valid():
        selection = form.cleaned_data.get('status')
        request.user.profile.languagePreference=selection
        request.user.profile.save()

    context = {'form': form,}
    return render(request, 'user/profile.html', context)

def myprofileview(request, username):
    profile = Profile.objects.get(user = request.user)
    return render(request,'user/profile.html',{'profile':profile})


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('settings:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = RegisterForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'user/editprofile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

