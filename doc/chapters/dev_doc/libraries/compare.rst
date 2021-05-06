==========
Compare.py
==========

La librairie compare.py permet la comparaison de deux fichiers au format csv.
Les données des fichiers doivent avoir pour séparateur le point virgule ";".




.. warning::

    Cette librairie est opérationnelle, mais sa structure n'est pas propre.

        - Les paramètres sont entrés au sein même du script, il seront exteriorisé.
        - Les appels de variables robotframework sont isolés à une sous méthode chacun, ils seront extériorisés.
        - L'utilisation des fichier csv ne se fait pas par la bibliothèque csv, la relecture en est difficile (à régler plus tard)


.. contents::

Prérequis :
-----------

compare.py utilise les packages :

    - robotframework 3.1.2
    - xlsxwriter 1.2.6 :

La librairie utilise des variables d'environnement de robotframework, elle ne peut être utilisée que depuis une execution de robotframework.
Auquel cas les méthodes concernées renverrons une exception avec valeur manquante.






Utilisation
-----------

La librairie est utilisé par robotframework, chaque méthode présentée constitue un keyword.
Les keywords ne constituent pas nécéssairement un test au sens propre, certains ont pour fonction de réaliser une action sous-jacente
au test lui-même. Dans ce cas, une note le relèvera.
L'ensemble des méthodes a été conçu pour renvoyer un log dans les cas d'erreurs et de réussites :

    - cas de réussite : un simple RAS, ou une info sur le résultat si le keyword ne constitue pas un test,
    - cas d'échec : un log explicatif pour l'utilisateur (et non développeur), ce peut être une situation de test non concluant ou une impossibilité de réaliser le test pour une raison de paramètres.

D'un point de vue code, une exception constitue un fail robotframework et renvoie le commentaire de l'exception.
Un log simple est le contenu des "print()" exécutés.

Paramètres de la librairie
--------------------------

Les paramètres se situent en tête du script sous forme de variables en UCC.
Ils peuvent être modifiés en cas de besoin.

.. csv-table:: Paramètres du fichier report
    :header-rows: 1

    Paramètre,Description, valeur par défaut
    ATTENDU_COLOR, bg des cellules contentant une donnée de l'attendu,'#FFFF66'
    RESULTAT_COLOR, bg des cellules contentant une donnée du résultat,'#D15509'
    IGNORED_VALUE_COLOR, bg des cellules des différences ignorées dans le fichier report,'#C7C2C2'
    ALIGN_CELL, alignement par défaut des cellules du tableau, 'center'
    REPORT_FILE_EXTENSION, extension par défaut du fichier report, ".xlsx"
    CELL_BORDER_SIZE, taille par défaut des bordures du tableau, 1

.. csv-table:: Paramètres des paths
    :header-rows: 1

    Paramètre,Description, valeur par défaut
    REPORT_LOG_DIR, nom du dossier stockant le report xlxs du keyword **Create Log Xlsx Compare File**, "report_log"
    PROJECT_REPERTORY, dossier du projet - par défaut le dossier parent au dossier courant, path.dirname(path.dirname(path.realpath(__file__)))

Keywords
--------

La librairie est conçue pour renvoyer une réponse sur comparaison entres deux fichiers csv dans toutes les situations.

Le keyword compare

.. csv-table:: Paramètres
    :header-rows: 1


    Paramètres,Type,valeur par défaut
    expected_file_path, file path,
    outgoing_file_path, file path,
    columns_to_exclude, numeric list [] (1rst column = 1), None

.. note::

    **Ce keyword ne constitue pas un test, mais permet de renvoyer une liste d'ecarts.**

Il compare champ par champ les deux fichiers. Il peut ignorer une liste de colonnes.
Elle exploite le contenu des fichiers mais **ne les modifie pas**.
Initialement elle trie les lignes de chaque fichier.
Répondant à un besoin robotframwork, dans le cas d'impossibilité de comparer les deux tableaux, elle renvoie une exception : un fail apparait dans RF :

    - le nombre de lignes différentes : elle renvoie dans le log le nombre de ligne pour chaque fichier.
    - le nombre de colonnes différente pour une ligne : elle renvoie un tableau indiquant les lignes concernées avec le nombre de colonne pour chaque

Si les tableaux correspondent, elle renvoie une liste d'ecarts sous le format

.. code-block::

    ((ligne, colonne),(valeur_du_champ_fichier1, valeur_du_champ_fichier2))

Cette liste peut être exploitée par les keywords :

    - Raise Differences
    - Create Log Xlsx Compare File


Le keyword Raise Differences

.. csv-table:: Paramètres
    :header-rows: 1

    Paramètres,Type,valeur par défaut
    tableau_de_differences, liste de tuples,

.. note::

    **Ce keyword constitue le test de comparaison. Son role est de renvoyer la conclusion du test**

Ce keyword prend en paramètres la liste d'ecarts renvoyée par le keyword Compare.
Il renvoie un fail si la liste n'est pas vide, avec en log le nombre de différences.

En cas de liste vide, elle renvoie en log "Aucune différences, test concluant !!"


Le keyword Create Log Xlsx Compare File


.. csv-table:: Paramètres
    :header-rows: 1

    Paramètres,Type,valeur par défaut
    expected_file, file path,
    outgoing_file, file path,
    diff_tab, tuple list,

.. note::

    **Ce keyword ne constitue pas un test. Il est un outil de facilitation de l'analyse des ecarts constatés.**


Ce keyword reprend les données des deux fichiers csv comparés ainsi que la liste des écarts retournée par la méthode compare.

    - Il renvoie un fichier xlsx dans le dossier REPORT_LOG_DIR, permettant une comparaison fine des deux fichiers expected_file et outgoing_file.
    - Il met en relief les différences relevées dans diff_tab.
    - Il met en gris les différences non relevées dans diff_tab (les différences volontairement ignorées).

Cas d'erreur
------------


.. code-block::

    get_value_from_name(), missing argument "name"


La méthode BuiltIn.get_value_from_name() prend en paramètre la variable robotframework concernée.
Dans le cas de cette erreur, cette variable est prise pour le premier paramètre implicite : l'environnement.
Cette méthode dépendant de l'environnement et du contexte de robotframework, elle ne fonctionne que lorsque la méthode souche est appelée en keyword dans un script .robot.
Pour palier à ce problème lors de la conception, il suffit de construire un bouchon correspondant à la variable RF dans les sous méthodes concernées.
La variable ne renvoie qu'un string dans les cas :

    - SUITE_SOURCE : path du dossier du testsuite en cours
    - SUITE_NAME : formatage du nom du test et de des dossiers parents de la forme Source.Du.Fichier.Nom Du Fichier ("_" changés en " ", tout en title)


