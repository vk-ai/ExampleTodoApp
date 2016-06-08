from django.forms import ModelForm
from Todo.models import User


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'password']
