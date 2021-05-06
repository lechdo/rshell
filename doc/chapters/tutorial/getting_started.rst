============
Installation
============

Les besoins d'ajout de librairies, de nouveaux tests, mais également les mise à
jour des librairies du projet ont conduit à simplifier le processus d'installation
et d'utilisation du projet.

Le lancement des tests s'effectue par ligne de commande uniquement.
L'installation est automatisée, mais peut être lancée manuellement sous chaque étape si
besoin.

Installation manuelle du projet

Installation ou réinstallation de l'environnement complet

Il faut pour cela exécuter le bash d'installation :

.. code-block::

    cd Installation
    bash install_libraries.sh

L'installation sera intégrale et supprimera l'environnement python
précédent s'il existait.


Mise à jour de l'environnement

La mise à jour ne réinstalle pas l'environnement, elle ré execute
simplement la liste des librairies dans le requirement.txt dans Installation.
Elle mets à jour également la liste des packages internes au projet, en
consultant la liste indiquée dans Config.ini.

.. code-block::

    # ne pas oublier de lancer l'environnement virtuel
    source robot_env/bin/activate
    python3.5 Libraries/tools/manage/install.py

.. warning::

    Pour toute manipulation de setup.py ou install.py, l'environnement
    virtuel est requis.
    Dans le cas contraire, aucune installation ne se fera par question
    d'intégrité du python racine.


