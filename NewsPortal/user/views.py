from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from .forms import UserForm
from django.contrib.auth.models import User
from news.models import Author, CategoryUser
from django.http import HttpResponse
from django.urls import reverse_lazy

@login_required
def degrade_me(request):
    user = request.user
    au_group = Group.objects.get(name='authors')
    if request.user.groups.filter(name='authors').exists():
        au_group.user_set.remove(user)
    Author.objects.filter(user_id=user.id).delete()
    return redirect('/user')

@login_required
def upgrade_me(request):
    user = request.user
    au_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        au_group.user_set.add(user)
    Author.objects.create(user_id=user.id)
    return redirect('/user')

@login_required
def sub_me(request, *args, **kwargs):
    CategoryUser.objects.create(category_id=kwargs['cat'], user_id=request.user.id)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def unsub_me(request, *args, **kwargs):
    CategoryUser.objects.filter(category_id=kwargs['cat'], user_id=request.user.id).delete()
    return redirect(request.META.get('HTTP_REFERER'))


class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class UserUpdate(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    model = User
    template_name = 'user_edit.html'
    def form_valid(self, form):
        self.success_url = '/user/'
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs) \
            if self.get_object().id == request.user.id else HttpResponse(status=403)

