from django import forms
import os
from core import settings
from .models import RegistrationToken, User
from django.contrib.auth.forms import AuthenticationForm

class ApartmentRegistrationForm(forms.ModelForm):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'lars@larsen.dk'}
            ),
        required=True,
        label='Email'
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'Lars'}
            ),
        required=True,
        label='Fornavn'
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'Larsen'}
            ),
        required=True,
        label='Efternavn'
    )
    token = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'Engangskode'}
            ),
        required=True,
        label='Engangskode',
        help_text='Indtast den engangskode du har fået fra bestyrelsen.',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'Kodeord'}
            ),
        required=True,
        label='Kodeord'
        )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'Bekræft kodeord'}
            ),
        required=True,
        label='Bekræft kodeord'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
        ]

    def clean_token(self):
        token_val = self.cleaned_data.get('token')
        try:
            self.token_obj = RegistrationToken.objects.get(
                token=token_val, is_used=False
            )
        except RegistrationToken.DoesNotExist:
            raise forms.ValidationError(
                'This invitation token is invalid or has already been used.'
            )
        return token_val

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        # Instead of manual setting, we leverage your UserManager!
        apartment = (
            self.token_obj.apartment if hasattr(self, 'token_obj') else None
        )

        if not commit:
            # If commit=False is requested, just return an unsaved instance
            user = User(
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                apartment=apartment,
            )
            user.set_password(self.cleaned_data['password'])
            return user

        # Otherwise, use your UserManager to create and save the user safely
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            apartment=apartment,
        )

        # Mark the token as used
        if hasattr(self, 'token_obj'):
            self.token_obj.is_used = True
            self.token_obj.save()

        return user

class CustomAuthenticationForm(AuthenticationForm):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Change the default 'Username' label to 'Email'
    self.fields['username'].label = 'Email'
    self.fields['username'].widget.attrs.update(
        {'class': 'input', 'type': 'email', 'placeholder': 'lars@larsen.dk'}
    )
    self.fields['password'].label = 'Kodeord'
    self.fields['password'].widget.attrs.update(
        {'class': 'input', 'type': 'password', 'placeholder': 'Kodeord'}
    )

class AccountUpdateForm(forms.ModelForm):
    default_picture_choice = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Or choose from preset avatars',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_pic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        memojis_dir = os.path.join(settings.MEDIA_ROOT, 'memojis')
        choices = [('', '-- Keep current avatar --')]

        if os.path.exists(memojis_dir):
            for filename in os.listdir(memojis_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    rel_path = f'memojis/{filename}'
                choices.append((rel_path, filename))

        self.fields['default_picture_choice'].choices = choices

    def save(self, commit=True):
        user = super().save(commit=False)
        chosen_default = self.cleaned_data.get('default_picture_choice')

        if chosen_default:
            user.profile_pic = chosen_default
        elif 'profile_pic' in self.changed_data and self.cleaned_data.get(
            'profile_pic'
        ):
        # If they uploaded a new custom file, use that instead
            user.profile_picture = self.cleaned_data['profile_pic']

        if commit:
            user.save()
        return user