from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Apartment
from posts.models import Post


class LandingPageView(TemplateView):
    template_name = 'landing.html'

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    title = 'Hjem'

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            posts = Post.objects.all()

            context["recent_posts"] = posts.order_by('-created_on')[:3]

            return context

class ApartmentsListView(LoginRequiredMixin, ListView):
    template_name = 'apartments.html'
    model = Apartment
    title = 'Lejligheder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        apartments = Apartment.objects.all()

        context["apartments"] = apartments.order_by('name')

        return context

