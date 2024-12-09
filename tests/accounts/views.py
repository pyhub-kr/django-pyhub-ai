from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

login = auth_views.LoginView.as_view(
    template_name="accounts/login.html",
    redirect_authenticated_user=True,
)


logout = auth_views.LogoutView.as_view(
    next_page="accounts:login",
)


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")


signup = SignupView.as_view()


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
