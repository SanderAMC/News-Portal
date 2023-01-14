from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms
from django.contrib.auth.models import User


class BasicSignupForm(SignupForm):

    first_name = forms.CharField(max_length=150, label='First Name', required=False)
    last_name = forms.CharField(max_length=150, label='Last Name', required=False)
    username = forms.CharField(max_length=150, label='Username', required=False)

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user


class UserForm(forms.ModelForm):
   class Meta:
       model = User
       fields = [
           'username',
           'email',
           'first_name',
           'last_name',
       ]

