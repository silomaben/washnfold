from django.contrib.auth.forms import UserChangeForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from base.models import Profile


class EditProfileForm(UserChangeForm):
    # Fields from User model are already included in UserChangeForm
    profilepic = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)
    contact = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_hire = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')  # Include fields from User model

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Check if there is an associated Profile
        if instance and instance.id:
            try:
                profile = Profile.objects.get(user=instance)
                self.fields['contact'].initial = profile.contact
                self.fields['date_of_hire'].initial = profile.date_of_hire
                # Add other fields from the Profile model
            except Profile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super(EditProfileForm, self).save(commit)

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile(user=user)

        profile.contact = self.cleaned_data['contact']
        profile.date_of_hire = self.cleaned_data['date_of_hire']
        # Set other fields from the Profile model

        if self.cleaned_data['profilepic']:
            profile.profile_pic = self.cleaned_data['profilepic']

        if commit:
            profile.save()

        return user