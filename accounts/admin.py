import os
from django import forms
from django.conf import settings
from django.contrib import admin
from .models import Apartment, RegistrationToken, User

class RegistrationTokenInline(admin.TabularInline):
    model = RegistrationToken
    extra = 0
    readonly_fields = ('token', 'is_used', 'created_at', 'created_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [RegistrationTokenInline]

@admin.register(RegistrationToken)
class RegistrationTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'apartment', 'is_used', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'created_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class CustomUserAdminForm(forms.ModelForm):
  default_picture_choice = forms.ChoiceField(
      required=False,
      label='Or pick from default gallery',
      help_text='Selecting an image here will override the current picture.',
  )

  class Meta:
    model = User
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Populate choices from media/avatars/defaults/
    memojis_dir = os.path.join(settings.MEDIA_ROOT, 'memojis')
    choices = [('', '-- Keep Current / Uploaded Picture --')]

    if os.path.exists(memojis_dir):
      for filename in os.listdir(memojis_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
          rel_path = f'memojis/{filename}'
          choices.append((rel_path, filename))

    self.fields['default_picture_choice'].choices = choices

  def save(self, commit=True):
    user = super().save(commit=False)
    chosen_default = self.cleaned_data.get('default_picture_choice')

    # If a default image was selected from dropdown and no file was explicitly uploaded
    if chosen_default and not self.cleaned_data.get('profile_pic'):
      user.profile_pic = chosen_default

    if commit:
      user.save()
    return user

# Register your custom user model using standard ModelAdmin (or leave it out if you don't need it in admin yet)
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'apartment', 'profile_pic', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'apartment')

