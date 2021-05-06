===================
Prérequis du projet
===================

.. warning::

    Le projet est supporté par python 3.X >= 3.5

.. note::

    Pour une question d'intégrité, le projet est testé et compatible sur
    des versions de 3.5 à 3.8. Platon étant équipé du 3.5, aucun outil
    python postérieur n'est utilisé.


modules
-------

la liste de ces modules est disponibles dans le fichier requirements.txt
L'ensemble des modules nécessaires sont fournis dans le dossier installation
le script ``Installation/install_libraries.sh`` permet l'installation de l'environnement dédié dans le projet.
    - **robotframework**
    - cx-Oracle
    - redis
    - robotframework-databaselibrary
    - xlsxwriter

    .. note::

        Prérequis pour la librairie compare.py

    - sphinx

    .. note::

        Ce module n'est pas un prérequis à lexécution du projet. Il est cependant utile à la conception pour mettre à jour
        la documentation. Aucun fichier d'installation n'est intégré au projet. Il doit être intégré manuellement en local.

