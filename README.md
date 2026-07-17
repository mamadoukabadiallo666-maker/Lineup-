# LineUp UI branding

Cette branche (feature/ui-branding) applique un rebranding visuel inspiré par Instagram : header centré, barre de recherche, icônes et styles modernes. Le nom de l'application reste "LineUp".

Fichiers ajoutés/modifiés:
- lineup/templates/base.html (mise à jour pour charger les assets statiques et nouveau header)
- static/css/main.css (styles principaux)
- static/img/logo.svg (logo placeholder avec gradient)

Comment tester localement:
1. Crée et active ton environnement virtuel.
2. Installe les dépendances (Django déjà utilisées).
3. Exécute `python manage.py collectstatic --noinput` si tu utilises collectstatic.
4. Lance le serveur: `python manage.py runserver` et visite `http://127.0.0.1:8000/`.

Si tu veux d'autres ajustements visuels (palette, icônes, intégration React/SPA), dis-le et je l'appliquerai.
