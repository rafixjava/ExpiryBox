from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    # UserCreationForm already has: username, password1 and password2.
    # We add name and email.
    first_name = forms.CharField(label="Name", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ["username", "first_name", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class AccountForm(forms.ModelForm):
    # Used on the "My account" page to change name and email.
    first_name = forms.CharField(label="Name", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ["first_name", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        # Is this email used by a DIFFERENT user?
        other_users = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if other_users.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class DeleteAccountForm(forms.Form):
    # The user must type their password before the account is deleted.
    password = forms.CharField(label="Type your password to confirm", widget=forms.PasswordInput)
