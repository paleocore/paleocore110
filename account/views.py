from django.shortcuts import render, redirect
from django.views import generic
from django.http import Http404
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .forms import RegistrationForm
from .models import UserInstitution
from .tokens import account_activation_token

class RegisterUser(generic.TemplateView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(edit_customer)
        return render(request, 'register_user.html', {'form': RegistrationForm()})

    def post(self, request):
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            try:
                user = registration_form.save(commit=False)
                user.is_active = False
                user.save()
                user.refresh_from_db()
                user.userinstitution.institution = registration_form.cleaned_data['institution']
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate Your Paleocore Account'
                message = render_to_string('account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)
                return render(request, 'register_user.html', {'registered': "Thanks for registering! Please check your email to confirm your account."})
            except Exception as e:
                # print("there was an exception")
                # import traceback
                # traceback.print_exc()
                registration_form.add_error(None, str(e))
                return render(request, 'register_user.html', {'form': registration_form})
        else:
            return render(request, 'register_user.html', {'form': registration_form})

class LoginUser(generic.TemplateView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(edit_customer)
        return render(request, 'login.html', {'form': AuthenticationForm()})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user_auth = authenticate(request, username=username, password=password)
        user = User.objects.filter(username=username).first()
        if user_auth is not None:
            login(request, user_auth)
            return redirect('/')
        elif user is not None and not user.userinstitution.email_confirmed:
            print(user)
            print(user.userinstitution.email_confirmed)
            return render(request, 'inactive.html')
        else:
            # Return an 'invalid login' error message. TODO
            return render(request, 'login.html', {'form': AuthenticationForm(), 'error': 'username or password incorrect'})

class PasswordReset(PasswordResetView):
    template_name = "password_reset.html"
    email_template_name = "password_reset_email.html"

class PasswordResetDone(PasswordResetDoneView):
    template_name = "password_reset_done.html"

class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"

class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"

def logout_user(request):
    logout(request)
    return redirect('/')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.userinstitution.email_confirmed = True
        user.userinstitution.save()
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return render(request, 'account_activation_invalid.html')

register_user = RegisterUser.as_view()
login_user = LoginUser.as_view()