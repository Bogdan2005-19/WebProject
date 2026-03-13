from django import forms
from .models import Review
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

from .models import *

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        help_text=''
    )
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        help_text=''
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        help_text=''
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
        help_text=''
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2')

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password is not None and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class CustomUserChangeForm(UserChangeForm):
    password = None  # Elimina el campo password

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar']
        help_texts = {field: '' for field in fields}

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if avatar:
            ext = avatar.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('Solo se permiten archivos JPG o PNG.')

        return avatar


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['titulo', 'texto', 'rating']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'floatingTitulo',
                'placeholder': 'Título de la reseña'
            }),
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'floatingContenido',
                'placeholder': 'Escribe tu reseña',
                'style': 'resize:none; height: 150px',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'floatingPuntuacion',
                'placeholder': 'Puntúa del 0 al 10',
                'min': 0,
                'max': 10
            }),
        }