from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import redirect, render

from .forms import AccountForm, DeleteAccountForm, RegisterForm


def register(request):
    # Someone who is already logged in doesn't need to register.
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Django saves the password as a secure hash
            login(request, user)
            messages.success(request, "Welcome to ExpiryBox! Your account has been created.")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        # AuthenticationForm checks that the username and password are correct.
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # If the user tried to open a private page first, the URL has
            # ?next=/that/page/ in it. Send them back there.
            next_page = request.GET.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect("dashboard")
    else:
        form = AuthenticationForm(request)

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    # We only log out on POST (when the "Log out" button is clicked).
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required
def account(request):
    if request.method == "POST":
        form = AccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account details were saved.")
            return redirect("account")
    else:
        form = AccountForm(instance=request.user)

    return render(request, "accounts/account.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Without this line the user would be logged out after changing the password.
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed.")
            return redirect("account")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def delete_account(request):
    if request.method == "POST":
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]

            if request.user.check_password(password):
                user = request.user
                logout(request)
                # Deleting the user also deletes their items, reminders,
                # notifications and impact records (on_delete=CASCADE).
                user.delete()
                messages.success(request, "Your account has been deleted.")
                return redirect("login")
            else:
                form.add_error("password", "The password is not correct.")
    else:
        form = DeleteAccountForm()

    return render(request, "accounts/delete_account.html", {"form": form})
