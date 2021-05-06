============
Installation
============


L'ensembles des librairies non custom sont au format ``tar.gz`` ou ``whl`` dans le dossier Installation.
Le projet n'étant pas monté depuis une machine ayant un accès internet, aucune spécification de version n'est
fournie, les versions sont celle intégrées au projet.

Liste des librairies actuelles requises:

    - robotframework - redislibrary
    - redis
    - robotframework
    - cx_oracle
    - robotframework-databaselibrary
    - xlsxwriter

De plus l'environnement étant monté depuis virtualenv, les librairies par défaut sont bien sûr présentes:

    - wheel
    - setuptools
    - pip


L'installation des librairies peut requérir certaines particulatités.

Librairies
----------

robotframwork
_____________

Le framework, aucune partircularité. Aucun pré requis dans l'environnement.
La version actuelle est 3.1.2, mise à jour pour :

- utilisation de kwargs (kwarg=value) dans les paramètres des keywords

la MAJ n'apporte pas de changements majeurs. RAS.


redis
_____

Utilisée pour la manipulation de redis, cette librairie n'est pas une librairie
RF, mais est nécéssaire pour les opérations effectuées.

Pour palier à son incompatiblité, une librairie custom ``redis_custom`` fait l'intermédiaire.
de ce fait **cette librairie n'est pas importée dans les scripts RF mais dans une autre librairie**.

cx_oracle
_________

Librairie officielle Oracle pour python. Non compatible avec RF.
Pour y palier l'ancienne version du projet utilisait DatabaseLibrary pour
permettre une connexion par API avec cx_oracle.
Cette méthode comporte des difficultés (logs, codes retour, debug, performance)
et a été remplacée par une librairie custom intermédiaire ``oracle_handler``.


.. warning::

    Actuellement DatabaseLibrary est toujours intégrée au projet mais ne semble pas
    utilisée. Elle sera retirée dans une version future.



xlsxwriter
__________

Cette librairie est non officielle. Elle est utilisée pour créer des rapports
xlsx lisibles sous windows.

Prérequis pour:

- compare.py


Environnement
-------------

Actuellement, l'environnement virtuel est créé par virtualenv.
L'usage de ce projet comprend donc le prérequis virtualenv sur le python3.5 de la machine.

Pour construire entièrement le venv, il faut:

- Créer l'environnement dans le dossier robot_env

        .. code-block:: shell

            virtualenv path/to/robot_env

- installer l'ensemble des librairies

        .. note::

            l'environnement peut s'exécuter avec le path du python/pip/autre
            dans le venv, mais pour plus de simplicité, on peut activer l'environnement

        .. code-block::

            robot_env/bin/pip install Installation/COMMON/
            robot_env/bin/pip install Installation/LINUX/