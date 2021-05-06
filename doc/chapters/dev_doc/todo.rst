==============================================
Liste des éléments à construire dans le projet
==============================================

Les TODOS du projet.


    - documentation

        - la structure (reprendre les readme dans chaque dossier)
        - le tutoriel

            - l'installation par git
            - l'installation par jenkins
            - le lancement des test simple
            - le lancement des test par jenkins

        - les librairies

            - les readme de lib
            - doc approfondie des nouvelles lib et report de ces infos dans le script (pour doc dev)
        - la doc utilisateur

            - les paramètres globaux
            - les sources pour les fichiers report et log

        - (optionnel) le design de la doc à améliorer.

    - librairies

        - compare.py

            - améliorer construction des méthode en utilisant le module csv
            - placer exceltools dans compare.py (librairie en 2 initialement pour raison de dev)
            - tests unitaires + doc de TU sauf pour la partie xlsx (besoin de l'env RF, peut être mettre un parametre "test" pour les réaliser ?)
            - extérioriser les paramètres, notamment l'appel des éléments relatif à l'environnement RF

        - ldi.py

            - extérioriser les paramètres, notamment l'appel des éléments relatif à l'environnement RF
            - ordonner plus clairement les méthodes dans le script
            - tests unitaires + doc de TU
            - méthode get_local_file() incomplète (fonctionnelle uniquement pour attendu et resultat); à compléter

    - makesoup.py

        - nommer plus professionnellement (et plus clairement)
        - créer doc
        - tests unitaires + doc de TU

