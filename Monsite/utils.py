from django.utils import timezone
from .models import Investissement, ProfilUtilisateur

def calcul_gain_journalier(investissement):
    """
    Calcule le gain journalier d'un investissement basé sur le pourcentage de gain journalier.
    """
    niveau = investissement.niveau
    return investissement.montant * (niveau.pourcentage_gain_journalier / 100)

def ajouter_gain_quotidien_au_solde(utilisateur):
    """
    Ajoute le gain quotidien au solde de l'utilisateur si cela n'a pas encore été fait aujourd'hui.
    """
    try:
        investissement_actif = Investissement.objects.get(utilisateur=utilisateur, actif=True)
        profil = ProfilUtilisateur.objects.get(utilisateur=utilisateur)

        # Vérifie si le gain quotidien a déjà été ajouté aujourd'hui
        derniere_mise_a_jour = investissement_actif.date_depot
        if derniere_mise_a_jour.date() < timezone.now().date():
            # Calcul du gain journalier et mise à jour du solde
            gain_journalier = calcul_gain_journalier(investissement_actif)
            profil.solde += gain_journalier
            profil.save()

            # Met à jour la date de dépôt pour enregistrer le dernier ajout
            investissement_actif.date_depot = timezone.now()
            investissement_actif.save()

    except (Investissement.DoesNotExist, ProfilUtilisateur.DoesNotExist):
        # Aucun investissement actif ou profil trouvé, rien à faire
        pass
