from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = CKEditor5Field('Text', config_name='extends')
    #content = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title + ' | ' + self.author.first_name + ' ' + self.author.last_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = self.title.lower()
            self.slug = slugify(base_slug)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return "/posts/%s/" % self.slug

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.first_name} on "{self.post.title}"'