from django import forms
from django.forms import ModelForm
from Todo.models import User


class LoginForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, max_length=128)

    class Meta:
        model = User
        fields = ['name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
