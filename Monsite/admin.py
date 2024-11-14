from django.contrib import admin
from .models import ProfilUtilisateur, Niveau, Investissement, Transaction,Paramètres

# Enregistrement du modèle Paramètres pour permettre la gestion dans l'administration
@admin.register(Paramètres)
class ParamètresAdmin(admin.ModelAdmin):
    # Liste des champs à afficher dans la liste des objets Paramètres
    list_display = ('CINETPAY_APIKEY', 'CINETPAY_SECRETE_KEY', 'CINETPAY_SITE_ID')
    # Configuration pour que l'interface d'administration n'ait qu'un seul objet Paramètres
    def has_add_permission(self, request):
        # Permet de n'avoir qu'une seule instance des paramètres
        return not Paramètres.objects.exists()


# Customisation de l'affichage de ProfilUtilisateur dans l'admin
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'parrain')

# Customisation de l'affichage de Niveau dans l'admin
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('nom', 'montant_min', 'pourcentage_gain_journalier')

# Customisation de l'affichage d'Investissement dans l'admin
class InvestissementAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'niveau', 'montant', 'date_depot', 'actif')
    list_filter = ('actif', 'niveau')

# Customisation de l'affichage de Transaction dans l'admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'montant', 'date', 'type_transaction')
    list_filter = ('type_transaction', 'date')

# Enregistrer les modèles dans l'admin
admin.site.register(ProfilUtilisateur, ProfilUtilisateurAdmin)
admin.site.register(Niveau, NiveauAdmin)
admin.site.register(Investissement, InvestissementAdmin)
admin.site.register(Transaction, TransactionAdmin)

