from django.db import models
from django.contrib.auth.models import User

# Étendre le modèle User pour inclure le parrain
class ProfilUtilisateur(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    parrain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='filleuls')
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Nouveau champ pour stocker le solde

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"

class Niveau(models.Model):
    nom = models.CharField(max_length=50)
    montant_min = models.DecimalField(max_digits=10, decimal_places=2)
    pourcentage_gain_journalier = models.DecimalField(max_digits=5, decimal_places=2)
    duree = models.IntegerField(default=30)  # Durée en jours

    def gain_total(self):
        # Calcul du gain total basé sur le pourcentage journalier et la durée
        return self.montant_min * (self.pourcentage_gain_journalier / 100) * self.duree


class Investissement(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depot = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

# Types de transactions pour distinguer les dépôts, gains, et retraits
class Transaction(models.Model):
    TYPES_TRANSACTION = [
        ('depot', 'Dépôt'),
        ('gain', 'Gain quotidien'),
        ('retrait', 'Retrait'),
        ('commission', 'Commission de parrainage')
    ]
    investissement = models.ForeignKey(Investissement, on_delete=models.CASCADE, null=True, blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    type_transaction = models.CharField(max_length=10, choices=TYPES_TRANSACTION)


class Paramètres(models.Model):
    CINETPAY_APIKEY = models.CharField(max_length=255, blank=True, null=True)
    CINETPAY_SECRETE_KEY = models.CharField(max_length=255, blank=True, null=True)
    CINETPAY_SITE_ID = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Paramètres globaux"
