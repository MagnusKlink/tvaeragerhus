from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf.urls.static import static
from .views import ApartmentRegistrationView, CustomLoginView, AccountView, AccountUpdateView, AccountsListView

urlpatterns = [
    path('', AccountsListView.as_view(), name='accounts_list'),
    path('register/', ApartmentRegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('<slug:slug>/', AccountView.as_view(), name='account'),
    path('<slug:slug>/update/', AccountUpdateView.as_view(), name='account_update'),
]