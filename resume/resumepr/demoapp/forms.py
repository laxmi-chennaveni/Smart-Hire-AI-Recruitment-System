from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# 1. రిజిస్ట్రేషన్ ఫామ్
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


# 2. లాగిన్ ఫామ్ (ఇది మిస్ అవ్వడం వల్లే ఇందాక ఎర్రర్ వచ్చింది)
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))