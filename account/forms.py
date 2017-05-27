from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    institution = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['institution'].required = True
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")
        username = self.cleaned_data.get('username')    

        if password1 != password2:
            msg = "passwords do not match"
            self.add_error('password', msg)
            self.add_error('confirm_password', msg)

        if len(password1) < 6 or len(password2) < 6:
            msg = "please enter 6 or more characters for password"
            self.add_error('password1', msg)
            self.add_error('password2', msg)

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            self.add_error('email', 'a user with that email already exists')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'institution', 'password1', 'password2')