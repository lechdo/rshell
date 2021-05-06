=======================
Fichiers de paramétrage
=======================

La réalisation de tests sur SGG demande l'execution de scripts bash.
Un grand nombre de ces scripts demandent des paramètres. Ceux ci dépendent du contexte,
ils diffèrent d'un test à l'autre. Cet ensemble de cas de paramétrage a été rassemblé dans plusieurs fichiers selon
les besoins.

Chaque fichier est exploité par un keyword du projet (voir function), ce fichier est explicitement nommé comme le keyword
concerné.
Chaque fichier représente un pattern de paramétrage. Sous format csv, ils transmette les information sous le format

    .. csv-table::
        :header-rows: 1

        id, parametre 1, parametre 2, parametre 3, ...

L'ordre est indiqué en introduction du fichier.
    - une colonne est un type de paramètre
    - chaque paramètre est obligatoire au fonctionnement du keyword
    - l'id est l'argument transmit au keyword pour qu'il s'execute.

