from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='نام کاربری', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'نام کاربری', 'id': 'username'}))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': ' رمز عبور', 'id': 'password'}))
