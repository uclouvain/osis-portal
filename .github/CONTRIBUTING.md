### Lisibilité du code :
- Séparation des classes: deux lignes vides
- Séparation des fonctions: une ligne vide
- print() interdit. Retirez-les avant le pull request

### Documentation du code :
- Documenter les fonctions (paramètres, fonctionnement, ce qu'elle renvoie)
- Ne pas hésiter à laisser une ligne de commentaire dans le code, décrivant brièvement le fonctionnement d'algorithme plus compliqué/plus longs

### Nomenclature :
- Toutes les variables et msgid (traduction) sont écrites en minuscules avec un '_' (underscore) comme séparateur

### Réutilisation du code :
- Ne pas créer de fonctions qui renvoient plus d'un seul paramètre (perte de contrôle sur ce que fait la fonction et perte de réutilisation du code)
- Ne pas faire de copier/coller ; tout code dupliqué ou faisant la même chose doit être implémenté dans une fonction documentée qui est réutilisable
- Ne pas utiliser de 'magic_number' (constante non déclarée dans une variable). Par exemple, pas de -1, 1994, 2015 dans le code, mais déclarer en haut du fichier des variables sous la forme LIMIT_START_DATE=1994, LIMIT_END_DATE=2015, etc.

### Performance :
- Ne pas faire d'appel à la DB (pas de queryset) dans une boucle 'for' :
    - Récupérer toutes les données nécessaires en une seule requête avant d'effectuer des opérations sur les attributs renvoyés par le Queryset
    - Si la requête doit récupérer des données dans plusieurs tables, utiliser le select_related fourni par Django (https://docs.djangoproject.com/en/1.9/ref/models/querysets/#select-related)
    - Forcer l'évaluation du Queryset avant d'effectuer des récupération de données avec *list(a_queryset)* 

### Modèle :
- Chaque fichier décrivant un modèle doit se trouver dans le répertoire *'models'*
- Chaque fichier contenant une classe du modèle ne peut renvoyer que des instances du modèle qu'elle déclare. Autrement dit, un fichier my_model.py contient une classe MyModel() et des méthodes qui ne peuvent renvoyer que des records venant de MyModel

### Formulaire :
- Utiliser les objets Forms fournis par Django (https://docs.djangoproject.com/en/1.9/topics/forms/)

### Sécurité :
- Ne pas laisser de données sensibles/privées dans les commentaires/dans le code

### Pull request :
- Ne fournir qu'un seul fichier de migration par issue/branche (fusionner tous les fichiers de migrations que vous avez en local en un seul fichier)
