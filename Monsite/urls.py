from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.contrib.auth import views as auth_views


app_name='Monsite'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('completer_profil/', views.completer_profil, name='completer_profil'),
    path('profil_utilisateur/', views.profil_utilisateur, name='profil_utilisateur'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('investissements/', views.liste_investissements, name='liste_investissements'),
    path('investissements/creer/', views.creer_investissement, name='creer_investissement'),
    path('investissements/<int:investissement_id>/creer-transaction/', views.creer_transaction, name='creer_transaction'),
    path('historique_transactions/', views.historique_transactions, name='historique_transactions'),
    path('assistance/', views.assistance, name='assistance'),
    path('portefeuille/', views.portefeuille, name='portefeuille'),
    path('inviter_amis/', views.inviter_amis, name='inviter_amis'),
    path('activer_niveau/', views.activer_niveau, name='activer_niveau'),
    path('deposer-fonds/', views.deposer_fonds, name='deposer_fonds'),
    path('verifier-depot/<str:transaction_id>/', views.verifier_depot, name='verifier_depot'),
    path('notification-depot/', views.notification_depot, name='notification_depot'),
    path('retirer-fonds/', views.retirer_fonds, name='retirer_fonds'),
    path('paiement_succes/', views.paiement_succes, name='paiement_succes'),
    path('initier_paiement/', views.initier_paiement, name='initier_paiement'),
    path('paiement_notification/', views.paiement_notification, name='paiement_notification'),
    path('paiement_erreur/', views.paiement_erreur, name='paiement_erreur'),
]
