from django.shortcuts import render
from .forms import ChangePasswordForm
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required

def changepassword(request):
    message = ""

    if request.method == "POST":
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            hashed_password = make_password(password)

            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC Sp_ChangePassword @username=%s, @password=%s",
                    [username, hashed_password]
                )

            message = "رمز عبور با موفقیت تغییر کرد."
        else:
            message = "رمز تغییر نکرد اشتباهی رخ است."

    else:
        # مقداردهی اولیه برای فرم (مثلاً از کاربر فعلی)
        initial_username = request.user.username if request.user.is_authenticated else ''
        form = ChangePasswordForm(initial={'username': initial_username})

    return render(request, "main/includes/change_password/change_password.html", {
        'form': form,
        'message': message,

    })
