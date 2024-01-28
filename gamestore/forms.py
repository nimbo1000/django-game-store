from allauth.account.forms import SignupForm
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django import forms
from django.contrib.auth.models import Group


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(CustomSocialAccountAdapter, self).save_user(request, sociallogin, form)
        group, _ = Group.objects.get_or_create(name='Gamer')
        group.user_set.add(user)
        group.save()
        return user


class RegistrationForm(SignupForm):
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)
    developer = forms.BooleanField(required=False)
    field_order = ['email', 'username','first_name', 'last_name', 'password1', 'password2', 'developer']

    def save(self, request):
        user = super(RegistrationForm, self).save(request)

        if self.cleaned_data['developer']:
            group, _ = Group.objects.get_or_create(name='Developer')
        else:
            group, _ = Group.objects.get_or_create(name='Gamer')

        group.user_set.add(user)

        return user


class PaymentForm(forms.Form):
    pid = forms.CharField(widget=forms.HiddenInput(), max_length=100)
    sid = forms.CharField(widget=forms.HiddenInput(), max_length=100)
    success_url = forms.URLField(widget=forms.HiddenInput())
    cancel_url = forms.URLField(widget=forms.HiddenInput())
    error_url = forms.URLField(widget=forms.HiddenInput())
    checksum = forms.CharField(widget=forms.HiddenInput(), max_length=32)
    amount = forms.CharField(widget=forms.HiddenInput(), max_length=32)
