from django.contrib.auth.forms import UserChangeForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.models import User
from django import forms


class EditProfileForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))
    username = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))
    # last_login = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))
    # ls_superuser = forms.CharField(max_length=100,widget=forms.CheckboxInput(attrs={'class':'form-check'}))
    # ls_staff = forms.CharField(max_length=100,widget=forms.CheckboxInput(attrs={'class':'form-check'}))
    # ls_active = forms.CharField(max_length=100,widget=forms.CheckboxInput(attrs={'class':'form-check'}))
    # date_joined = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))
    

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email', 'password')