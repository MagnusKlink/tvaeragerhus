from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from .forms import ApartmentRegistrationForm, CustomAuthenticationForm, AccountUpdateForm
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class ApartmentRegistrationView(CreateView):
    model = User
    form_class = ApartmentRegistrationForm
    template_name = (
        'register.html'
    )
    success_url = reverse_lazy(
        'home'
    ) 

    def get_initial(self):
        """Pre-populates the token field if a user clicks a link like

        /register/?token=uuid-string-here
        """
        initial = super().get_initial()
        token_param = self.request.GET.get('token')
        if token_param:
            initial['token'] = token_param
        return initial

    def form_valid(self, form):
        # form.save() triggers the custom save method we wrote in the form,
        # which hashes the password, links the apartment, and marks the token used.
        response = super().form_valid(form)

        # Automatically log the user in immediately after registration
        login(self.request, self.object)

        return response

class CustomLoginView(LoginView):
  form_class = CustomAuthenticationForm
  template_name = 'login.html' 
  redirect_authenticated_user = (
      True  # Redirects away from login page if already logged in
  )

class AccountView(LoginRequiredMixin, DetailView):
    template_name = 'account.html'
    model = User
    title = 'Profil'

class AccountsListView(LoginRequiredMixin, ListView):
    template_name = 'accounts_list.html'
    model = User
    title = 'Beboere'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        accounts = User.objects.all()

        context["accounts"] = accounts.order_by('-first_name')

        return context

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AccountUpdateForm
    template_name = 'account_update.html'
    title = 'Opdatér profil'

    # Tell Django to look up the user by the 'slug' field using the 'slug' URL parameter
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        # Fetch the object based on the slug in the URL
        obj = super().get_object(queryset)

        # Security check: ensure users can only edit their own profile
        if obj != self.request.user:
            raise PermissionDenied(
            'You do not have permission to edit this profile.'
        )

        return obj

    def get_success_url(self):
        # Redirect back to their profile detail page using their slug
        return reverse('account', kwargs={'slug': self.object.slug})