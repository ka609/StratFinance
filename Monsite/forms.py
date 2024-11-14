from django import forms
from .models import Investissement
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProfilUtilisateur


class InscriptionForm(UserCreationForm):
    parrain_username = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Username du parrain (facultatif)', 'class': 'form-control', 'aria-label': 'Parrain'
    }))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'parrain_username']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur', 'class': 'form-control',
                                               'aria-label': 'Nom d\'utilisateur'}),
            'password1': forms.PasswordInput(
                attrs={'placeholder': 'Mot de passe', 'class': 'form-control', 'aria-label': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe', 'class': 'form-control',
                                                    'aria-label': 'Confirmation du mot de passe'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        parrain_username = self.cleaned_data.get('parrain_username')
        parrain = User.objects.filter(username=parrain_username).first() if parrain_username else None

        if commit:
            user.save()
            profil, created = ProfilUtilisateur.objects.get_or_create(utilisateur=user, defaults={'parrain': parrain})
            if not created and parrain:  # Si le profil existe déjà, mettez à jour le parrain si nécessaire
                profil.parrain = parrain
                profil.save()

        return user


# Formulaire pour créer un investissement
class InvestissementForm(forms.ModelForm):
    class Meta:
        model = Investissement
        fields = ['utilisateur', 'niveau', 'montant']

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant < 1000:
            raise forms.ValidationError("Le montant minimum de dépôt est de 1000 FCFA.")
        return montant

class CompleterProfilForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Prénom', 'class': 'form-control', 'aria-label': 'Prénom'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Nom', 'class': 'form-control', 'aria-label': 'Nom'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email', 'class': 'form-control', 'aria-label': 'Email'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']