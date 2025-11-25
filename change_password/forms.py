from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='نام کاربری', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'نام کاربری', 'id': 'username'}))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': ' رمز عبور', 'id': 'password'}))


class ChangePasswordForm(forms.Form):
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام کاربری',
            'id': 'username',
            'readonly': 'readonly',
            'style': 'width: 300px;'
        })
    )
    password = forms.CharField(
        label='رمز عبور',
        min_length='8',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور',
            'id': 'password',
            'style': 'width: 300px;'
        })
    )
