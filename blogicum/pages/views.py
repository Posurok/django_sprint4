from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def page_500(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=""):
    return render(request, 'pages/403csrf.html', status=403)
