import uuid
import os
import random
import shortuuid
from shortuuid.django_fields import ShortUUIDField
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.text import slugify

def get_random_default_memoji():
  """Returns a relative media path to a random image in media/memojis/."""
  memojis_dir = os.path.join(settings.MEDIA_ROOT, 'memojis')
  if os.path.exists(memojis_dir):
    images = [
        f
        for f in os.listdir(memojis_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]
    if images:
      chosen = random.choice(images)
      return f'memojis/{chosen}'
  return 'memojis/default.png'

def profile_pic_upload_to(instance, filename):
    return "profile_pics/{}/{}".format(instance.id, filename)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    apartment = models.ForeignKey(
        'Apartment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    profile_pic = models.ImageField(
        default=get_random_default_memoji, 
        blank=True,
        null=True,
        upload_to=profile_pic_upload_to, 
        help_text=("Upload an image to personalize your profile"))
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.slug and self.email:
            # Convert email to a URL-safe slug format (e.g., user@example.com -> user-at-example.com)
            base_slug = self.email.replace('@', '-at-').lower()
            self.slug = slugify(base_slug)

        if self.pk:
            try:
                old = self.__class__.objects.get(pk=self.pk)
                if old.profile_pic and old.profile_pic != self.profile_pic:
                    old.profile_pic.delete(save=False)
            except self.__class__.DoesNotExist:
                pass

        super().save(*args, **kwargs)

class Apartment(models.Model):
    class ApartmentNumber(models.IntegerChoices):
        N_55 = 55, "Nummer 55"
        N_57 = 57, "Nummer 57"
        N_59 = 59, "Nummer 59"
        N_61 = 61, "Nummer 61"
        N_63 = 63, "Nummer 63"
        N_65 = 65, "Nummer 65"
        N_67 = 67, "Nummer 67"
        N_69 = 69, "Nummer 69"

    class ApartmentLevel(models.TextChoices):
            ST = "St.", "Stuen"
            FIRST = "1.", "Første"

    class ApartmentSide(models.TextChoices):
        TV = "Tv.", "Til venstre"
        TH = "Th.", "Til højre"

    number = models.IntegerField(choices=ApartmentNumber.choices, default=ApartmentNumber.N_55)

    level = models.CharField(max_length=10, choices=ApartmentLevel.choices, default=ApartmentLevel.ST)

    side = models.CharField(max_length=10, choices=ApartmentSide.choices, default=ApartmentSide.TV)


    name = models.CharField(max_length=50, editable=False)

    def save(self, *args, **kwargs):
        self.name = f"{self.number}, {self.level} {self.side}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class RegistrationToken(models.Model):
    apartment = models.ForeignKey(
        Apartment, on_delete=models.CASCADE, related_name='tokens'
    )
    token = ShortUUIDField(length=8, editable=False, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f'Token for {self.apartment.name} ({self.token})'

